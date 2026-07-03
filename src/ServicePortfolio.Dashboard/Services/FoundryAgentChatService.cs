using System.Runtime.CompilerServices;
using System.Text;
using Microsoft.Extensions.Options;
using ServicePortfolio.Dashboard.Models;

namespace ServicePortfolio.Dashboard.Services;

public sealed class FoundryAgentChatService : IAgentChatService
{
    private readonly IFoundryAgentClient _client;
    private readonly IDashboardDataService _dashboardDataService;
    private readonly FoundryAgentOptions _options;
    private readonly ILogger<FoundryAgentChatService> _logger;

    public FoundryAgentChatService(
        IFoundryAgentClient client,
        IDashboardDataService dashboardDataService,
        IOptions<FoundryAgentOptions> options,
        ILogger<FoundryAgentChatService> logger)
    {
        _client = client;
        _dashboardDataService = dashboardDataService;
        _options = options.Value;
        _logger = logger;
    }

    public string CreateConversationId() => Guid.NewGuid().ToString("N");

    public async IAsyncEnumerable<string> SendMessageAsync(
        string conversationId,
        string message,
        [EnumeratorCancellation] CancellationToken cancellationToken = default)
    {
        if (!HasRequiredSettings())
        {
            yield return "Foundry Agent の接続設定が未完了です。`FoundryAgent:ProjectEndpoint` と `FoundryAgent:AgentId` または `FoundryAgent:AgentName` を設定してください。";
            yield break;
        }

        string response;
        string? errorMessage = null;
        try
        {
            var prompt = await BuildGroundedPromptAsync(message, cancellationToken);
            response = await _client.SendMessageAsync(conversationId, prompt, cancellationToken);
        }
        catch (OperationCanceledException)
        {
            throw;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Foundry Agent chat failed for conversation {ConversationId}", conversationId);
            response = string.Empty;
            errorMessage = "Foundry Agent への問い合わせ中にエラーが発生しました。Azure認証、Agent設定、Search接続を確認してください。";
        }

        if (errorMessage is not null)
        {
            yield return errorMessage;
            yield break;
        }

        foreach (var chunk in SplitForStreaming(response))
        {
            cancellationToken.ThrowIfCancellationRequested();
            yield return chunk;
        }
    }

    private bool HasRequiredSettings()
    {
        return !string.IsNullOrWhiteSpace(_options.ProjectEndpoint)
            && (!string.IsNullOrWhiteSpace(_options.AgentId) || !string.IsNullOrWhiteSpace(_options.AgentName));
    }

    private async Task<string> BuildGroundedPromptAsync(string message, CancellationToken cancellationToken)
    {
        var summary = await _dashboardDataService.GetDashboardSummaryAsync(cancellationToken);
        var context = BuildDashboardContext(summary);

        return $$"""
            あなたはサービス資産化の経営判断を支援するチャットエージェントです。
            役割は、ダッシュボードの読み上げではなく、候補の優先理由、ICE内訳、候補比較、判断条件の整理、90日アクション、根拠確認を深掘りすることです。
            数値・順位・候補名はダッシュボード事実を優先し、元データにない売上予測、市場規模、正式な投資判断、根拠のないSaaS化推奨は行わないでください。
            条件変更の質問では、正式ICEではなく「仮の評価条件によるシミュレーション」と明示してください。
            案件や文書の根拠は接続済みの Azure AI Search から取得し、根拠が不十分な場合は推測せず、不足している確認事項を明示してください。

            ## ダッシュボード事実
            {{context}}

            ## ユーザーの質問
            {{message}}
            """;
    }

    private static string BuildDashboardContext(DashboardSummary summary)
    {
        var builder = new StringBuilder();
        builder.AppendLine($"総案件数: {summary.TotalProjects}");
        builder.AppendLine($"サービス候補数: {summary.ServiceCandidateCount}");
        builder.AppendLine($"受注売上合計: {summary.TotalContractedSales:N0} 円");
        builder.AppendLine($"平均利益率: {summary.AverageProfitMargin:F1}%");
        builder.AppendLine($"分析ステータス: {summary.AnalysisStatus}");

        foreach (var candidate in summary.ServiceCandidates.OrderBy(candidate => candidate.Rank).Take(5))
        {
            builder.AppendLine();
            builder.AppendLine($"候補{candidate.Rank}: {candidate.Name}");
            builder.AppendLine($"優先度: {candidate.Priority}");
            builder.AppendLine($"根拠案件数: {candidate.Metrics.SupportingProjectCount}");
            builder.AppendLine($"受注率: {candidate.Metrics.WinRate:F1}%");
            builder.AppendLine($"平均利益率: {candidate.Metrics.AverageMarginRate:F1}%");
            builder.AppendLine($"推奨モデル: {candidate.RecommendedBusinessModelLabel}");
            builder.AppendLine($"要約: {candidate.ExecutiveSummary}");
        }

        return builder.ToString().Trim();
    }

    private static IEnumerable<string> SplitForStreaming(string response)
    {
        if (string.IsNullOrWhiteSpace(response))
        {
            yield return "Foundry Agent から空の応答が返されました。";
            yield break;
        }

        var normalized = response.Replace("\r\n", "\n", StringComparison.Ordinal);
        foreach (var paragraph in normalized.Split("\n\n", StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries))
        {
            yield return paragraph + "\n\n";
        }
    }
}