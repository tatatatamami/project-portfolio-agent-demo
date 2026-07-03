namespace ServicePortfolio.Dashboard.Models;

public sealed record SourceEvidenceDetails
{
    public required string SourceId { get; init; }
    public string DocumentKind { get; init; } = string.Empty;
    public string CandidateId { get; init; } = string.Empty;
    public string CandidateName { get; init; } = string.Empty;
    public string ProjectId { get; init; } = string.Empty;
    public string ProjectName { get; init; } = string.Empty;
    public string Industry { get; init; } = string.Empty;
    public string EvidenceSummary { get; init; } = string.Empty;
    public IReadOnlyList<string> RelatedSourceIds { get; init; } = [];
}