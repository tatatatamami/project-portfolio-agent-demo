namespace ServicePortfolio.Dashboard.Services;

public sealed class FoundryAgentOptions
{
    public string ProjectEndpoint { get; init; } = string.Empty;
    public string AgentId { get; init; } = string.Empty;
    public string AgentName { get; init; } = string.Empty;
    public string ApiVersion { get; init; } = "2025-05-01";
    public string TokenScope { get; init; } = "https://ai.azure.com/.default";
    public int TimeoutSeconds { get; init; } = 90;
    public int PollingIntervalMilliseconds { get; init; } = 1000;
    public int MaxPollingAttempts { get; init; } = 60;
}