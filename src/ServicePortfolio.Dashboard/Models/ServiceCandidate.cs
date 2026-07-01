namespace ServicePortfolio.Dashboard.Models;

public sealed record ServiceCandidate
{
    public required string Name { get; init; }
    public int Rank { get; init; }
    public double Priority { get; init; }
    public string Rationale { get; init; } = string.Empty;
    public string RecommendedBusinessModel { get; init; } = string.Empty;
    public int IndustryCount { get; init; }
    public double ReuseRatePct { get; init; }
    public double TotalWonRevenueJPYBillion { get; init; }
    public double WinRate { get; init; }
    public double AverageProfitMargin { get; init; }
    public double AverageEffortReductionRate { get; init; }
    public IReadOnlyList<string> SupportingProjects { get; init; } = [];
    public IReadOnlyList<string> ReuseAssets { get; init; } = [];
    public IReadOnlyList<string> RequiredPreparation { get; init; } = [];
    public int AssetizationStageIndex { get; init; }
    public IReadOnlyList<string> CommonRequirements { get; init; } = [];
    public IReadOnlyList<string> MajorRisks { get; init; } = [];
    public string NextManagementDecision { get; init; } = string.Empty;
}
