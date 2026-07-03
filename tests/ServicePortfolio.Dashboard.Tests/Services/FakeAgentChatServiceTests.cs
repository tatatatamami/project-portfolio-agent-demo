using Microsoft.Extensions.Logging.Abstractions;
using ServicePortfolio.Dashboard.Models;
using ServicePortfolio.Dashboard.Services;

namespace ServicePortfolio.Dashboard.Tests.Services;

public class FakeAgentChatServiceTests
{
    private readonly FakeAgentChatService _sut = new(new StubDashboardDataService(), NullLogger<FakeAgentChatService>.Instance);

    [Fact]
    public void CreateConversationId_ReturnsNonEmptyString()
    {
        var id = _sut.CreateConversationId();
        Assert.False(string.IsNullOrWhiteSpace(id));
    }

    [Fact]
    public void CreateConversationId_ReturnsUniqueIds()
    {
        var id1 = _sut.CreateConversationId();
        var id2 = _sut.CreateConversationId();
        Assert.NotEqual(id1, id2);
    }

    [Fact]
    public async Task SendMessageAsync_ReturnsNonEmptyResponse()
    {
        var chunks = new List<string>();
        await foreach (var chunk in _sut.SendMessageAsync("conv-1", "根拠を教えて"))
        {
            chunks.Add(chunk);
        }
        Assert.NotEmpty(chunks);
        Assert.False(string.IsNullOrWhiteSpace(string.Concat(chunks)));
    }

    [Fact]
    public async Task SendMessageAsync_RespondsToKnownKeyword_根拠()
    {
        var result = await CollectResponseAsync("根拠案件を教えてください");
        Assert.Contains("根拠案件", result);
        Assert.Contains("P001", result);
    }

    [Fact]
    public async Task SendMessageAsync_RespondsToKnownKeyword_比較()
    {
        var result = await CollectResponseAsync("1位と2位を比較してください");
        Assert.Contains("1位と2位の比較", result);
        Assert.Contains("候補A", result);
        Assert.Contains("候補B", result);
    }

    [Fact]
    public async Task SendMessageAsync_RespondsToKnownKeyword_ICE()
    {
        var result = await CollectResponseAsync("ICEスコアの内訳を説明してください");
        Assert.Contains("ICE内訳", result);
        Assert.Contains("Impact", result);
        Assert.Contains("Confidence", result);
        Assert.Contains("Ease", result);
    }

    [Fact]
    public async Task SendMessageAsync_RespondsToKnownKeyword_90日()
    {
        var result = await CollectResponseAsync("次の90日で何を決めるべきですか");
        Assert.Contains("次の90日", result);
        Assert.Contains("成功条件", result);
    }

    [Fact]
    public async Task SendMessageAsync_UnknownMessage_ReturnsFallbackResponse()
    {
        var result = await CollectResponseAsync("全く無関係なメッセージ");
        Assert.NotEmpty(result);
    }

    [Fact]
    public async Task SendMessageAsync_CancellationToken_ThrowsOperationCanceledException()
    {
        using var cts = new CancellationTokenSource();
        cts.Cancel();

        await Assert.ThrowsAsync<OperationCanceledException>(async () =>
        {
            await foreach (var _ in _sut.SendMessageAsync("conv-1", "test", cts.Token))
            {
            }
        });
    }

    private async Task<string> CollectResponseAsync(string message)
    {
        var chunks = new List<string>();
        await foreach (var chunk in _sut.SendMessageAsync("conv-1", message))
        {
            chunks.Add(chunk);
        }
        return string.Concat(chunks);
    }

    private sealed class StubDashboardDataService : IDashboardDataService
    {
        public Task<DashboardSummary> GetDashboardSummaryAsync(CancellationToken cancellationToken = default) => Task.FromResult(new DashboardSummary
        {
            TotalProjects = 2,
            ServiceCandidateCount = 2,
            TotalContractedSales = 300_000_000m,
            AverageProfitMargin = 25.0,
            AnalysisStatus = "completed",
            ServiceCandidates =
            [
                CreateCandidate("CAND-001", 1, "候補A", 92, 100, 30.0, 200_000_000m, "P001"),
                CreateCandidate("CAND-002", 2, "候補B", 70, 75, 20.0, 100_000_000m, "P002")
            ]
        });

        private static ServiceCandidate CreateCandidate(string candidateId, int rank, string name, int priority, double winRate, double margin, decimal revenue, string projectId) => new()
        {
            CandidateId = candidateId,
            Rank = rank,
            Name = name,
            ExecutiveSummary = $"{name}の要約",
            BusinessReason = $"{name}の理由",
            Scores = new CandidateScores { Priority = priority, Profitability = 80, Reusability = 70, Standardization = 60, RecurringRevenue = 50, SaasReadiness = 65, Feasibility = 75, Confidence = 90 },
            Ice = new CandidateIce
            {
                Score = priority,
                Impact = new IceAxis { Score = 90, Summary = "事業効果が高い", Factors = [new IceFactor { Name = "受注率", Value = $"{winRate:F1}%", Contribution = 20 }] },
                Confidence = new IceAxis { Score = 88, Summary = "根拠が十分", Factors = [new IceFactor { Name = "根拠案件数", Value = "2案件", Contribution = 16 }] },
                Ease = new IceAxis { Score = 70, Summary = "標準化確認が必要", Factors = [new IceFactor { Name = "Highリスク負荷", Value = "2件", Contribution = 8 }] },
                CalculationMethod = "normalized-geometric-mean",
                FormulaVersion = "ice-v1"
            },
            Metrics = new CandidateMetrics { SupportingProjectCount = 2, IndustryCount = 2, WinRate = winRate, AverageMarginRate = margin, AverageEffortReductionRate = 30, WonRevenue = revenue },
            RecommendedBusinessModel = new RecommendedBusinessModel { Current = "Standard Offering", Next = "Managed Service", FutureOption = "SaaS" },
            SupportingProjects = [new SupportingProject { ProjectId = projectId, ProjectName = $"{name} Project", Industry = "Retail", EvidenceSummary = "根拠", SourceIds = [$"DOC-{projectId}-RFP"] }],
            StandardizationGaps = [new StandardizationGap { Category = "Delivery", CurrentState = "個別", TargetState = "標準", Effort = "Medium", Priority = "High", Dependency = "レビュー", SourceIds = [$"DOC-{projectId}-RFP"] }],
            Risks = [new CandidateRisk { Name = "Risk", Impact = "Medium", Likelihood = "Medium", Mitigation = "責任範囲を明確化する", SourceIds = [$"DOC-{projectId}-RFP"] }],
            ManagementDecision = new ManagementDecision
            {
                Decision = "標準化検討を開始する",
                InvestmentLevel = "Medium",
                TimeHorizon = "90 days",
                Next90Days = [new EvidenceText { Text = "標準スコープを定義する", SourceIds = [$"DOC-{projectId}-RFP"] }],
                SuccessCriteria = [new EvidenceText { Text = "標準提案テンプレートが完成", SourceIds = [$"DOC-{projectId}-RFP"] }],
                StopOrReviewCriteria = [new EvidenceText { Text = "案件固有対応が主要工数を占める", SourceIds = [$"DOC-{projectId}-RFP"] }]
            }
        };
    }
}
