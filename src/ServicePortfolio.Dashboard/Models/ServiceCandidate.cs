namespace ServicePortfolio.Dashboard.Models;

public sealed record ServiceCandidate
{
    public required string Name { get; init; }
    public int Rank { get; init; }
    public double WinRate { get; init; }
    public double AverageProfitMargin { get; init; }
    public double AverageEffortReductionRate { get; init; }
    public IReadOnlyList<string> SupportingProjects { get; init; } = [];
    public IReadOnlyList<string> CommonRequirements { get; init; } = [];
    public IReadOnlyList<string> MajorRisks { get; init; } = [];
    public string NextManagementDecision { get; init; } = string.Empty;
}
