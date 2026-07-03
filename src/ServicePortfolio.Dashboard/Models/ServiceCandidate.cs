namespace ServicePortfolio.Dashboard.Models;

public sealed record ServiceCandidate
{
    public required string CandidateId { get; init; }
    public required string Name { get; init; }
    public int Rank { get; init; }
    public string ExecutiveSummary { get; init; } = string.Empty;
    public IReadOnlyList<string> ExecutiveSummarySourceIds { get; init; } = [];
    public string BusinessReason { get; init; } = string.Empty;
    public IReadOnlyList<string> BusinessReasonSourceIds { get; init; } = [];
    public CandidateScores Scores { get; init; } = new();
    public CandidateIce? Ice { get; init; }
    public CandidateMetrics Metrics { get; init; } = new();
    public RecommendedBusinessModel RecommendedBusinessModel { get; init; } = new();
    public IReadOnlyList<SupportingProject> SupportingProjects { get; init; } = [];
    public IReadOnlyList<ReusableAsset> ReusableAssets { get; init; } = [];
    public IReadOnlyList<StandardizationGap> StandardizationGaps { get; init; } = [];
    public IReadOnlyList<EvidenceText> SuccessFactors { get; init; } = [];
    public IReadOnlyList<EvidenceText> FailureFactors { get; init; } = [];
    public IReadOnlyList<CandidateRisk> Risks { get; init; } = [];
    public ManagementDecision ManagementDecision { get; init; } = new();

    public int Priority => Ice?.Score ?? Scores.Priority;
    public string RecommendedBusinessModelLabel => string.Join(" → ", new[]
    {
        RecommendedBusinessModel.Current,
        RecommendedBusinessModel.Next,
        RecommendedBusinessModel.FutureOption
    }.Where(value => !string.IsNullOrWhiteSpace(value)));
}

public sealed record CandidateIce
{
    public int Score { get; init; }
    public IceAxis Impact { get; init; } = new();
    public IceAxis Confidence { get; init; } = new();
    public IceAxis Ease { get; init; } = new();
    public string CalculationMethod { get; init; } = string.Empty;
    public string FormulaVersion { get; init; } = string.Empty;
}

public sealed record IceAxis
{
    public int Score { get; init; }
    public string Summary { get; init; } = string.Empty;
    public IReadOnlyList<IceFactor> Factors { get; init; } = [];
}

public sealed record IceFactor
{
    public string Name { get; init; } = string.Empty;
    public string Value { get; init; } = string.Empty;
    public int Contribution { get; init; }
}

public sealed record CandidateScores
{
    public int Priority { get; init; }
    public int Profitability { get; init; }
    public int Reusability { get; init; }
    public int Standardization { get; init; }
    public int RecurringRevenue { get; init; }
    public int SaasReadiness { get; init; }
    public int Feasibility { get; init; }
    public int Confidence { get; init; }
}

public sealed record CandidateMetrics
{
    public int SupportingProjectCount { get; init; }
    public int IndustryCount { get; init; }
    public double WinRate { get; init; }
    public double AverageMarginRate { get; init; }
    public double AverageEffortReductionRate { get; init; }
    public decimal WonRevenue { get; init; }
}

public sealed record RecommendedBusinessModel
{
    public string Current { get; init; } = string.Empty;
    public string Next { get; init; } = string.Empty;
    public string FutureOption { get; init; } = string.Empty;
    public string Rationale { get; init; } = string.Empty;
    public IReadOnlyList<string> SourceIds { get; init; } = [];
}

public sealed record SupportingProject
{
    public string ProjectId { get; init; } = string.Empty;
    public string ProjectName { get; init; } = string.Empty;
    public string Industry { get; init; } = string.Empty;
    public string EvidenceSummary { get; init; } = string.Empty;
    public IReadOnlyList<string> SourceIds { get; init; } = [];
}

public sealed record ReusableAsset
{
    public string Name { get; init; } = string.Empty;
    public string Type { get; init; } = string.Empty;
    public int OccurrenceCount { get; init; }
    public int TotalProjectCount { get; init; }
    public int ReadinessScore { get; init; }
    public string CurrentState { get; init; } = string.Empty;
    public string NextAction { get; init; } = string.Empty;
    public IReadOnlyList<string> SourceIds { get; init; } = [];
}

public sealed record StandardizationGap
{
    public string Category { get; init; } = string.Empty;
    public string CurrentState { get; init; } = string.Empty;
    public string TargetState { get; init; } = string.Empty;
    public string Effort { get; init; } = string.Empty;
    public string Priority { get; init; } = string.Empty;
    public string Dependency { get; init; } = string.Empty;
    public IReadOnlyList<string> SourceIds { get; init; } = [];
}

public sealed record CandidateRisk
{
    public string Name { get; init; } = string.Empty;
    public string Impact { get; init; } = string.Empty;
    public string Likelihood { get; init; } = string.Empty;
    public string Mitigation { get; init; } = string.Empty;
    public IReadOnlyList<string> SourceIds { get; init; } = [];
}

public sealed record ManagementDecision
{
    public string Decision { get; init; } = string.Empty;
    public IReadOnlyList<string> DecisionSourceIds { get; init; } = [];
    public string InvestmentLevel { get; init; } = string.Empty;
    public string TimeHorizon { get; init; } = string.Empty;
    public IReadOnlyList<EvidenceText> Next90Days { get; init; } = [];
    public IReadOnlyList<EvidenceText> SuccessCriteria { get; init; } = [];
    public IReadOnlyList<EvidenceText> StopOrReviewCriteria { get; init; } = [];
}

public sealed record EvidenceText
{
    public string Text { get; init; } = string.Empty;
    public IReadOnlyList<string> SourceIds { get; init; } = [];
}
