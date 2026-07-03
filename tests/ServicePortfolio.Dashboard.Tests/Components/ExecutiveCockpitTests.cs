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
        Assert.Contains("ICE優先度 92", cut.Markup);
        Assert.Contains("Impact", cut.Markup);
        Assert.Contains("Confidence", cut.Markup);
        Assert.Contains("Ease", cut.Markup);
        Assert.Contains("受注率", cut.Markup);
        Assert.Contains("候補Aの理由", cut.Markup);
        Assert.Contains("根拠 1 件", cut.Markup);
        Assert.Contains("DOC-001", cut.Markup);

        cut.FindAll(".candidate-item")[1].Click();

        Assert.Contains("候補Bの理由", cut.Markup);
        Assert.DoesNotContain("候補Aの理由", cut.Find(".detail-rationale").TextContent);
    }

    [Fact]
    public void ExecutiveCockpit_ReportsSourceEvidenceWhenSourceIdIsClicked()
    {
        Services.AddSingleton<IDashboardDataService>(new StubDashboardDataService(CreateSummary()));
        SourceEvidenceDetails? clickedEvidence = null;

        var cut = RenderComponent<ExecutiveCockpit>(parameters => parameters
            .Add(component => component.OnSourceIdClicked, evidence => clickedEvidence = evidence));

        cut.Find("button.source-id-chip").Click();

        Assert.NotNull(clickedEvidence);
        Assert.Equal("DOC-001", clickedEvidence.SourceId);
        Assert.Equal("候補A", clickedEvidence.CandidateName);
        Assert.Equal("P001", clickedEvidence.ProjectId);
        Assert.Equal("Project 1", clickedEvidence.ProjectName);
        Assert.Equal("Retail", clickedEvidence.Industry);
        Assert.Equal("分析根拠文書", clickedEvidence.DocumentKind);
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

    [Fact]
    public void ExecutiveCockpit_DoesNotCrashWhenIceDataIsMissing()
    {
        var summary = CreateSummary() with
        {
            ServiceCandidates =
            [
                CreateCandidate("CAND-001", 1, "候補A", "候補Aの理由", 92) with { Ice = null }
            ]
        };
        Services.AddSingleton<IDashboardDataService>(new StubDashboardDataService(summary));

        var cut = RenderComponent<ExecutiveCockpit>();

        Assert.Contains("ICE優先度 92", cut.Markup);
        Assert.Contains("legacy", cut.Markup);
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
        ExecutiveSummarySourceIds = ["DOC-001"],
        BusinessReason = reason,
        BusinessReasonSourceIds = ["DOC-001"],
        Scores = new CandidateScores { Priority = priority, Profitability = 80, Reusability = 70, Standardization = 60, RecurringRevenue = 50, SaasReadiness = 40, Feasibility = 90, Confidence = 100 },
        Ice = new CandidateIce
        {
            Score = priority,
            Impact = new IceAxis { Score = 95, Summary = "事業効果", Factors = [new IceFactor { Name = "受注率", Value = "75.0%", Contribution = 15 }] },
            Confidence = new IceAxis { Score = 96, Summary = "成功確度", Factors = [new IceFactor { Name = "根拠案件", Value = "1案件", Contribution = 25 }] },
            Ease = new IceAxis { Score = 82, Summary = "実行容易性", Factors = [new IceFactor { Name = "必要投資レベル", Value = "Medium=60", Contribution = 6 }] },
            CalculationMethod = "normalized-geometric-mean",
            FormulaVersion = "ice-v1"
        },
        Metrics = new CandidateMetrics { SupportingProjectCount = 1, IndustryCount = 1, WinRate = 75, AverageMarginRate = 20, AverageEffortReductionRate = 30, WonRevenue = 100_000_000m },
        RecommendedBusinessModel = new RecommendedBusinessModel { Current = "Standard Offering", Next = "Managed Service", FutureOption = "SaaS", Rationale = "段階的に展開", SourceIds = ["DOC-001"] },
        SupportingProjects = [new SupportingProject { ProjectId = "P001", ProjectName = "Project 1", Industry = "Retail", EvidenceSummary = "根拠", SourceIds = ["DOC-001"] }],
        ReusableAssets = [new ReusableAsset { Name = "Asset", Type = "Feature", OccurrenceCount = 1, TotalProjectCount = 1, ReadinessScore = 80, CurrentState = "利用済み", NextAction = "標準化", SourceIds = ["DOC-001"] }],
        StandardizationGaps = [new StandardizationGap { Category = "Delivery", CurrentState = "個別", TargetState = "標準", Effort = "Medium", Priority = "High", Dependency = "レビュー", SourceIds = ["DOC-001"] }],
        SuccessFactors = [new EvidenceText { Text = "成功要因", SourceIds = ["DOC-001"] }],
        FailureFactors = [new EvidenceText { Text = "失敗要因", SourceIds = ["DOC-001"] }],
        Risks = [new CandidateRisk { Name = "Risk", Impact = "Medium", Likelihood = "Low", Mitigation = "対策", SourceIds = ["DOC-001"] }],
        ManagementDecision = new ManagementDecision
        {
            Decision = "投資判断する",
            DecisionSourceIds = ["DOC-001"],
            InvestmentLevel = "Medium",
            TimeHorizon = "90 days",
            Next90Days = [new EvidenceText { Text = "実行", SourceIds = ["DOC-001"] }],
            SuccessCriteria = [new EvidenceText { Text = "成功", SourceIds = ["DOC-001"] }],
            StopOrReviewCriteria = [new EvidenceText { Text = "見直し", SourceIds = ["DOC-001"] }]
        }
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