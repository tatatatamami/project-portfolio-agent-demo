namespace ServicePortfolio.Dashboard.Services;

public interface IAgentChatService
{
    string CreateConversationId();
    IAsyncEnumerable<string> SendMessageAsync(
        string conversationId,
        string message,
        CancellationToken cancellationToken = default);
}
