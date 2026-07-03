namespace ServicePortfolio.Dashboard.Services;

public interface IFoundryAgentClient
{
    Task<string> SendMessageAsync(
        string conversationId,
        string message,
        CancellationToken cancellationToken = default);
}