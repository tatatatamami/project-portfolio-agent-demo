namespace ServicePortfolio.Dashboard.Models;

public sealed record PortfolioAnalysisData
{
    public AnalysisRunInfo AnalysisRun { get; init; } = new();
    public DashboardSummaryData DashboardSummary { get; init; } = new();
    public IReadOnlyList<ServiceCandidate> Candidates { get; init; } = [];
}

public sealed record AnalysisRunInfo
{
    public string RunId { get; init; } = string.Empty;
    public string Status { get; init; } = string.Empty;
    public DateTimeOffset? GeneratedAt { get; init; }
    public int SourceProjectCount { get; init; }
    public string ModelProvider { get; init; } = string.Empty;
    public string ModelDeployment { get; init; } = string.Empty;
    public string PromptVersion { get; init; } = string.Empty;
}

public sealed record DashboardSummaryData
{
    public int ProjectCount { get; init; }
    public int CandidateCount { get; init; }
    public decimal WonRevenue { get; init; }
    public double AverageMarginRate { get; init; }
}