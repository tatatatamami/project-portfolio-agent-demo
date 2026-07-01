namespace ServicePortfolio.Dashboard.Models;

public sealed record DashboardSummary
{
    public int TotalProjects { get; init; }
    public int ServiceCandidateCount { get; init; }
    public decimal TotalContractedSales { get; init; }
    public double AverageProfitMargin { get; init; }
    public DateTimeOffset? GeneratedAt { get; init; }
    public string ModelProvider { get; init; } = string.Empty;
    public string ModelDeployment { get; init; } = string.Empty;
    public string AnalysisStatus { get; init; } = string.Empty;
    public string? ErrorMessage { get; init; }
    public IReadOnlyList<ServiceCandidate> ServiceCandidates { get; init; } = [];

    public bool HasError => !string.IsNullOrWhiteSpace(ErrorMessage);
    public bool HasAnalysisResults => ServiceCandidates.Count > 0;
}
