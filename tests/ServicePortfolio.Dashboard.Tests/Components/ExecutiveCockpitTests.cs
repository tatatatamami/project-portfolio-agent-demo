using Bunit;
using Microsoft.Extensions.DependencyInjection;
using ServicePortfolio.Dashboard.Components.ExecutiveCockpit;
using ServicePortfolio.Dashboard.Models;
using ServicePortfolio.Dashboard.Services;

namespace ServicePortfolio.Dashboard.Tests.Components;

public sealed class ExecutiveCockpitTests : TestContext
{
    [Fact]
    public void ExecutiveCockpit_RendersCandidatesAndSwitchesDetailsOnSelection()
    {
        Services.AddSingleton<IDashboardDataService>(new StubDashboardDataService(CreateSummary()));

        var cut = RenderComponent<ExecutiveCockpit>();

        Assert.Contains("分析対象案件", cut.Markup);
        Assert.Contains("候補A", cut.Markup);
        Assert.Contains("候補Aの理由", cut.Markup);

        cut.FindAll(".candidate-item")[1].Click();

        Assert.Contains("候補Bの理由", cut.Markup);
        Assert.DoesNotContain("候補Aの理由", cut.Find(".detail-rationale").TextContent);
    }

    [Fact]
    public void ExecutiveCockpit_ShowsEmptyMessageWhenNoCandidatesExist()
    {
        Services.AddSingleton<IDashboardDataService>(new StubDashboardDataService(new DashboardSummary
        {
            AnalysisStatus = "completed",
            ServiceCandidates = []
        }));

        var cut = RenderComponent<ExecutiveCockpit>();

        Assert.Contains("分析結果がありません", cut.Markup);
    }

    private static DashboardSummary CreateSummary() => new()
    {
        TotalProjects = 2,
        ServiceCandidateCount = 2,
        TotalContractedSales = 300_000_000m,
        AverageProfitMargin = 20.0,
        GeneratedAt = DateTimeOffset.Parse("2026-07-01T23:04:41Z"),
        ModelProvider = "azure-openai",
        ModelDeployment = "gpt-4.1",
        AnalysisStatus = "completed",
        ServiceCandidates =
        [
            CreateCandidate("CAND-001", 1, "候補A", "候補Aの理由", 92),
            CreateCandidate("CAND-002", 2, "候補B", "候補Bの理由", 88)
        ]
    };

    private static ServiceCandidate CreateCandidate(string candidateId, int rank, string name, string reason, int priority) => new()
    {
        CandidateId = candidateId,
        Rank = rank,
        Name = name,
        ExecutiveSummary = $"{name}の要約",
        BusinessReason = reason,
        Scores = new CandidateScores { Priority = priority, Profitability = 80, Reusability = 70, Standardization = 60, RecurringRevenue = 50, SaasReadiness = 40, Feasibility = 90, Confidence = 100 },
        Metrics = new CandidateMetrics { SupportingProjectCount = 1, IndustryCount = 1, WinRate = 75, AverageMarginRate = 20, AverageEffortReductionRate = 30, WonRevenue = 100_000_000m },
        RecommendedBusinessModel = new RecommendedBusinessModel { Current = "Standard Offering", Next = "Managed Service", FutureOption = "SaaS", Rationale = "段階的に展開" },
        SupportingProjects = [new SupportingProject { ProjectId = "P001", ProjectName = "Project 1", Industry = "Retail", EvidenceSummary = "根拠", SourceIds = ["DOC-001"] }],
        ReusableAssets = [new ReusableAsset { Name = "Asset", Type = "Feature", OccurrenceCount = 1, TotalProjectCount = 1, ReadinessScore = 80, CurrentState = "利用済み", NextAction = "標準化" }],
        StandardizationGaps = [new StandardizationGap { Category = "Delivery", CurrentState = "個別", TargetState = "標準", Effort = "Medium", Priority = "High", Dependency = "レビュー" }],
        SuccessFactors = ["成功要因"],
        FailureFactors = ["失敗要因"],
        Risks = [new CandidateRisk { Name = "Risk", Impact = "Medium", Likelihood = "Low", Mitigation = "対策" }],
        ManagementDecision = new ManagementDecision { Decision = "投資判断する", InvestmentLevel = "Medium", TimeHorizon = "90 days", Next90Days = ["実行"], SuccessCriteria = ["成功"], StopOrReviewCriteria = ["見直し"] }
    };

    private sealed class StubDashboardDataService : IDashboardDataService
    {
        private readonly DashboardSummary _summary;

        public StubDashboardDataService(DashboardSummary summary)
        {
            _summary = summary;
        }

        public Task<DashboardSummary> GetDashboardSummaryAsync(CancellationToken cancellationToken = default) => Task.FromResult(_summary);
    }
}