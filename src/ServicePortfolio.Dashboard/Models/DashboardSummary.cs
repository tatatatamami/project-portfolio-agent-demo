namespace ServicePortfolio.Dashboard.Models;

public sealed record DashboardSummary
{
    public int TotalProjects { get; init; }
    public int ServiceCandidateCount { get; init; }
    public decimal TotalContractedSales { get; init; }
    public double AverageProfitMargin { get; init; }
    public IReadOnlyList<ServiceCandidate> ServiceCandidates { get; init; } = [];
}
