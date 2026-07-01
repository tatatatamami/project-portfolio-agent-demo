using Microsoft.Extensions.Logging.Abstractions;
using ServicePortfolio.Dashboard.Services;

namespace ServicePortfolio.Dashboard.Tests.Services;

public class FakeAgentChatServiceTests
{
    private readonly FakeAgentChatService _sut = new(NullLogger<FakeAgentChatService>.Instance);

    [Fact]
    public void CreateConversationId_ReturnsNonEmptyString()
    {
        var id = _sut.CreateConversationId();
        Assert.False(string.IsNullOrWhiteSpace(id));
    }

    [Fact]
    public void CreateConversationId_ReturnsUniqueIds()
    {
        var id1 = _sut.CreateConversationId();
        var id2 = _sut.CreateConversationId();
        Assert.NotEqual(id1, id2);
    }

    [Fact]
    public async Task SendMessageAsync_ReturnsNonEmptyResponse()
    {
        var chunks = new List<string>();
        await foreach (var chunk in _sut.SendMessageAsync("conv-1", "根拠を教えて"))
        {
            chunks.Add(chunk);
        }
        Assert.NotEmpty(chunks);
        Assert.False(string.IsNullOrWhiteSpace(string.Concat(chunks)));
    }

    [Fact]
    public async Task SendMessageAsync_RespondsToKnownKeyword_根拠()
    {
        var result = await CollectResponseAsync("このサービス候補を優先する根拠は何ですか");
        Assert.Contains("根拠", result);
    }

    [Fact]
    public async Task SendMessageAsync_RespondsToKnownKeyword_成功()
    {
        var result = await CollectResponseAsync("成功案件と失注案件の違いを説明してください");
        Assert.Contains("成功", result);
    }

    [Fact]
    public async Task SendMessageAsync_RespondsToKnownKeyword_リスク()
    {
        var result = await CollectResponseAsync("サービス化前に確認すべきリスクは何ですか");
        Assert.Contains("リスク", result);
    }

    [Fact]
    public async Task SendMessageAsync_RespondsToKnownKeyword_経営アクション()
    {
        var result = await CollectResponseAsync("次の経営アクションを3点に絞ってください");
        Assert.Contains("アクション", result);
    }

    [Fact]
    public async Task SendMessageAsync_UnknownMessage_ReturnsFallbackResponse()
    {
        var result = await CollectResponseAsync("全く無関係なメッセージ");
        Assert.NotEmpty(result);
    }

    [Fact]
    public async Task SendMessageAsync_CancellationToken_ThrowsOperationCanceledException()
    {
        using var cts = new CancellationTokenSource();
        cts.Cancel();

        await Assert.ThrowsAsync<OperationCanceledException>(async () =>
        {
            await foreach (var _ in _sut.SendMessageAsync("conv-1", "test", cts.Token))
            {
            }
        });
    }

    private async Task<string> CollectResponseAsync(string message)
    {
        var chunks = new List<string>();
        await foreach (var chunk in _sut.SendMessageAsync("conv-1", message))
        {
            chunks.Add(chunk);
        }
        return string.Concat(chunks);
    }
}
