using System.Runtime.CompilerServices;
using Microsoft.Extensions.Logging;
using ServicePortfolio.Dashboard.Models;

namespace ServicePortfolio.Dashboard.Services;

public sealed class FakeAgentChatService : IAgentChatService
{
    private readonly IDashboardDataService _dashboardDataService;
    private readonly ILogger<FakeAgentChatService> _logger;

    public FakeAgentChatService(IDashboardDataService dashboardDataService, ILogger<FakeAgentChatService> logger)
    {
        _dashboardDataService = dashboardDataService;
        _logger = logger;
    }

    public string CreateConversationId() => Guid.NewGuid().ToString("N");

    public async IAsyncEnumerable<string> SendMessageAsync(
        string conversationId,
        string message,
        [EnumeratorCancellation] CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("FakeAgent processing message in conversation {ConversationId}", conversationId);

        var summary = await _dashboardDataService.GetDashboardSummaryAsync(cancellationToken);
        var response = SelectResponse(summary, message);
        var chunks = SplitForStreaming(response);

        foreach (var chunk in chunks)
        {
            cancellationToken.ThrowIfCancellationRequested();
            await Task.Delay(30, cancellationToken);
            yield return chunk;
        }
    }

    private static string SelectResponse(DashboardSummary summary, string message)
    {
        var candidates = summary.ServiceCandidates.OrderBy(candidate => candidate.Rank).ToArray();
        if (candidates.Length == 0)
            return "分析済みのサービス候補がないため、チャットで深掘りできる対象がありません。";

        var normalized = message.ToLowerInvariant();
        if (ContainsAny(normalized, "比較", "1位と2位", "二位", "2位")) return BuildComparisonResponse(candidates);
        if (ContainsAny(normalized, "ice", "impact", "confidence", "ease", "内訳", "算出", "低い理由", "上げる")) return BuildIceBreakdownResponse(candidates[0], normalized);
        if (ContainsAny(normalized, "saas", "不足", "阻害", "ギャップ")) return BuildSaasGapResponse(candidates[0]);
        if (ContainsAny(normalized, "90日", "経営判断", "決める", "部門", "チェック")) return BuildDecisionResponse(candidates[0]);
        if (ContainsAny(normalized, "根拠案件", "根拠", "source", "文書", "利益率")) return BuildEvidenceResponse(candidates[0]);
        if (ContainsAny(normalized, "投資余力", "6か月", "managed service", "利益率を最重要", "シミュレーション")) return BuildSimulationResponse(candidates, normalized);
        if (ContainsAny(normalized, "なぜ", "最優先", "優先", "1位")) return BuildPriorityResponse(candidates);

        return """
            ## このチャットで深掘りできること

            ダッシュボードの数値を前提に、経営判断の理由・比較・具体化を支援します。元データにない売上予測や正式な投資判断は行いません。

            - なぜこの候補が最優先なのか
            - ICEスコアの内訳
            - 1位と2位の比較
            - SaaS化に不足している要素
            - 次の90日の経営判断
            - 根拠案件とsourceId
            """;
    }

    private static string BuildPriorityResponse(IReadOnlyList<ServiceCandidate> candidates)
    {
        var top = candidates[0];
        var runnerUp = candidates.Count > 1 ? candidates[1] : null;
        var ice = top.Ice;

        return string.Join(Environment.NewLine, [
            $"## {top.Name} が最優先の理由",
            string.Empty,
            $"最優先の理由は、{top.Metrics.SupportingProjectCount}件・{top.Metrics.IndustryCount}業種で根拠があり、受注率{top.Metrics.WinRate:F1}%、平均利益率{top.Metrics.AverageMarginRate:F1}%、受注売上{FormatRevenue(top.Metrics.WonRevenue)}が確認できるためです。",
            string.Empty,
            $"- Impact: {ice?.Impact.Score ?? top.Scores.Profitability}。{ice?.Impact.Summary ?? "事業効果を評価しています。"}",
            $"- Confidence: {ice?.Confidence.Score ?? top.Scores.Confidence}。{ice?.Confidence.Summary ?? "根拠案件とデータ量から評価しています。"}",
            $"- Ease: {ice?.Ease.Score ?? top.Scores.Feasibility}。{ice?.Ease.Summary ?? "実行容易性を評価しています。"}",
            runnerUp is null ? "- 他候補比較: 比較対象の候補がありません。" : $"- 他候補比較: {runnerUp.Name} はICE {runnerUp.Priority} で、{top.Name} のICE {top.Priority} を下回ります。{top.Name} は収益性・再利用性・受注実績の一貫性で優位です。",
            "- 追加確認: 価格モデル、運用責任分界、標準提供範囲、パイロット顧客の適合条件は事業化前に確認が必要です。",
            string.Empty,
            "直ちにSaaS化を確定するのではなく、まず標準オファリングとして提供範囲と再利用資産を固める判断が妥当です。"
        ]);
    }

    private static string BuildIceBreakdownResponse(ServiceCandidate candidate, string message)
    {
        if (candidate.Ice is null)
            return $"## ICEスコアの内訳\n\n{candidate.Name} には詳細なICE内訳がありません。補助スコアでは優先度 {candidate.Priority} です。";

        return string.Join(Environment.NewLine, [
            $"## {candidate.Name} のICE内訳",
            string.Empty,
            $"総合ICEは **{candidate.Ice.Score}** です。これは Impact、Confidence、Ease を掛け合わせて正規化した参考評価です。",
            string.Empty,
            AxisSection("Impact", candidate.Ice.Impact),
            AxisSection("Confidence", candidate.Ice.Confidence),
            AxisSection("Ease", candidate.Ice.Ease),
            "### 経営向けの読み替え",
            $"{candidate.Name} は事業効果と分析確信度が高い一方、Easeはリスクや標準化ギャップの影響を受けます。Confidenceを上げるには、追加案件で同じ構成が再利用できるか、文書・実績・運用条件を継続して蓄積することが必要です。"
        ]);
    }

    private static string BuildComparisonResponse(IReadOnlyList<ServiceCandidate> candidates)
    {
        if (candidates.Count < 2) return "比較できる候補が2件未満です。";
        var first = candidates[0];
        var second = candidates[1];

        return string.Join(Environment.NewLine, [
            $"## 1位と2位の比較",
            string.Empty,
            $"| 観点 | 1位: {first.Name} | 2位: {second.Name} |",
            "|---|---:|---:|",
            $"| ICE | {first.Priority} | {second.Priority} |",
            $"| 受注率 | {first.Metrics.WinRate:F1}% | {second.Metrics.WinRate:F1}% |",
            $"| 平均利益率 | {first.Metrics.AverageMarginRate:F1}% | {second.Metrics.AverageMarginRate:F1}% |",
            $"| 受注売上 | {FormatRevenue(first.Metrics.WonRevenue)} | {FormatRevenue(second.Metrics.WonRevenue)} |",
            $"| 根拠案件 | {first.Metrics.SupportingProjectCount}件・{first.Metrics.IndustryCount}業種 | {second.Metrics.SupportingProjectCount}件・{second.Metrics.IndustryCount}業種 |",
            $"| SaaS適合 | {first.Scores.SaasReadiness} | {second.Scores.SaasReadiness} |",
            string.Empty,
            $"{first.Name} は収益性・再利用性・受注実績の一貫性で優位です。{second.Name} は事業効果では劣る一方、提供範囲を限定しやすく、短期の商品化やManaged Service化の検討に向いています。"
        ]);
    }

    private static string BuildSaasGapResponse(ServiceCandidate candidate)
    {
        var gaps = candidate.StandardizationGaps.Take(3).Select(gap => $"- {gap.Category}: 現在は「{gap.CurrentState}」。目標は「{gap.TargetState}」。優先度 {gap.Priority} / 工数 {gap.Effort}。");
        var risks = candidate.Risks.Take(3).Select(risk => $"- {risk.Name}: {risk.Mitigation}");

        return string.Join(Environment.NewLine, [
            $"## {candidate.Name} をSaaS化するために不足している要素",
            string.Empty,
            "現時点では、SaaS化を直ちに確定するより、標準オファリングからManaged Serviceへ進める方が現実的です。不足要素は次の通りです。",
            string.Empty,
            "### 標準化ギャップ",
            ..gaps,
            string.Empty,
            "### リスク・確認事項",
            ..risks,
            string.Empty,
            "### 優先して整備すること",
            "1. 標準提供範囲と除外条件",
            "2. 価格・契約モデル",
            "3. 運用責任分界と監視・改善サイクル",
            "4. 将来SaaS化する場合のテナント分離・データ分離方針"
        ]);
    }

    private static string BuildDecisionResponse(ServiceCandidate candidate)
    {
        var decision = candidate.ManagementDecision;
        var actions = decision.Next90Days.Take(3).Select((action, index) => $"{(index + 1) * 30}日以内: {action.Text}");

        return string.Join(Environment.NewLine, [
            $"## 次の90日で決めるべきこと",
            string.Empty,
            $"経営判断: {decision.Decision}",
            $"投資規模: {decision.InvestmentLevel} / 時間軸: {decision.TimeHorizon}",
            string.Empty,
            "### 推奨アクション",
            ..actions,
            string.Empty,
            "### 成功条件",
            ..decision.SuccessCriteria.Take(3).Select(item => $"- {item.Text}"),
            string.Empty,
            "### 中止・見直し条件",
            ..decision.StopOrReviewCriteria.Take(3).Select(item => $"- {item.Text}"),
            string.Empty,
            "### 巻き込む部門",
            "- 事業責任者: 提供範囲と投資判断",
            "- Delivery / PMO: 標準手順と成果物粒度",
            "- Sales: パイロット顧客と価格仮説",
            "- Operations: 運用責任分界と継続収益化"
        ]);
    }

    private static string BuildEvidenceResponse(ServiceCandidate candidate)
    {
        var projects = candidate.SupportingProjects.Select(project => $"- `{project.ProjectId}`: {project.ProjectName}（{project.Industry}） sourceId: {string.Join(", ", project.SourceIds)}");
        return string.Join(Environment.NewLine, [
            $"## {candidate.Name} の根拠案件",
            string.Empty,
            $"受注率 {candidate.Metrics.WinRate:F1}%、平均利益率 {candidate.Metrics.AverageMarginRate:F1}%、受注売上 {FormatRevenue(candidate.Metrics.WonRevenue)} は、以下の根拠案件から集計しています。",
            string.Empty,
            ..projects,
            string.Empty,
            "現在のJSONでは案件ID、案件名、業種、指標、sourceIdまで確認できます。提案書や振り返り本文の引用は、Foundry IQ / Azure AI Search 接続後に拡張する想定です。"
        ]);
    }

    private static string BuildSimulationResponse(IReadOnlyList<ServiceCandidate> candidates, string message)
    {
        var ranked = message.Contains("利益率", StringComparison.OrdinalIgnoreCase)
            ? candidates.OrderByDescending(candidate => candidate.Metrics.AverageMarginRate)
            : candidates.OrderByDescending(candidate => candidate.Scores.Feasibility + candidate.Scores.SaasReadiness);

        return string.Join(Environment.NewLine, [
            "## 条件変更による参考シミュレーション",
            string.Empty,
            "これは正式なICE評価ではありません。元のICEスコアは変更せず、仮の評価条件で並べ替えた参考結果です。",
            string.Empty,
            ..ranked.Select((candidate, index) => $"{index + 1}. {candidate.Name}: ICE {candidate.Priority} / 利益率 {candidate.Metrics.AverageMarginRate:F1}% / 実現性 {candidate.Scores.Feasibility} / SaaS適合 {candidate.Scores.SaasReadiness}"),
            string.Empty,
            "正式な投資判断には、提供開始までの実工数、価格仮説、運用責任分界、パイロット顧客の条件確認が必要です。"
        ]);
    }

    private static string AxisSection(string label, IceAxis axis)
    {
        return string.Join(Environment.NewLine, [
            $"### {label}: {axis.Score}",
            axis.Summary,
            ..axis.Factors.Take(5).Select(factor => $"- {factor.Name}: {factor.Value}（寄与 +{factor.Contribution}）"),
            string.Empty
        ]);
    }

    private static string FormatRevenue(decimal value) => $"{value / 100_000_000m:F1}億円";

    private static bool ContainsAny(string text, params string[] keywords) =>
        keywords.Any(keyword => text.Contains(keyword, StringComparison.OrdinalIgnoreCase));

    private static IReadOnlyList<string> SplitForStreaming(string response) =>
        response.Replace("\r\n", "\n", StringComparison.Ordinal)
            .Split("\n\n", StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries)
            .Select(paragraph => paragraph + "\n\n")
            .ToArray();
}
