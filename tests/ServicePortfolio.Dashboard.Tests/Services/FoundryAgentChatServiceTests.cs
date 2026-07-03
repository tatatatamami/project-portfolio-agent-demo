using Microsoft.Extensions.Logging.Abstractions;
using Microsoft.Extensions.Options;
using ServicePortfolio.Dashboard.Models;
using ServicePortfolio.Dashboard.Services;

namespace ServicePortfolio.Dashboard.Tests.Services;

public sealed class FoundryAgentChatServiceTests
{
    [Fact]
    public void CreateConversationId_ReturnsUniqueIds()
    {
        var sut = CreateService(new StubFoundryAgentClient("ok"), new FoundryAgentOptions
        {
            ProjectEndpoint = "https://example.services.ai.azure.com/api/projects/demo",
            AgentId = "asst_123"
        });

        var id1 = sut.CreateConversationId();
        var id2 = sut.CreateConversationId();

        Assert.False(string.IsNullOrWhiteSpace(id1));
        Assert.NotEqual(id1, id2);
    }

    [Fact]
    public async Task SendMessageAsync_WhenSettingsAreMissing_ReturnsConfigurationMessage()
    {
        var client = new StubFoundryAgentClient("should not be called");
        var sut = CreateService(client, new FoundryAgentOptions());

        var response = await CollectResponseAsync(sut, "根拠を教えて");

        Assert.Contains("接続設定が未完了", response);
        Assert.False(client.WasCalled);
    }

    [Fact]
    public async Task SendMessageAsync_SendsDashboardContextAndQuestionToClient()
    {
        var client = new StubFoundryAgentClient("## 回答\n\n候補Aを優先します。");
        var sut = CreateService(client, new FoundryAgentOptions
        {
            ProjectEndpoint = "https://example.services.ai.azure.com/api/projects/demo",
            AgentId = "asst_123"
        });

        var response = await CollectResponseAsync(sut, "優先根拠は何ですか");

        Assert.Contains("候補Aを優先", response);
        Assert.Contains("候補A", client.LastMessage);
        Assert.Contains("優先根拠は何ですか", client.LastMessage);
        Assert.Contains("Azure AI Search", client.LastMessage);
    }

    [Fact]
    public async Task SendMessageAsync_WhenClientThrows_ReturnsFriendlyErrorMessage()
    {
        var sut = CreateService(new ThrowingFoundryAgentClient(), new FoundryAgentOptions
        {
            ProjectEndpoint = "https://example.services.ai.azure.com/api/projects/demo",
            AgentName = "service-portfolio-chat-agent"
        });

        var response = await CollectResponseAsync(sut, "リスクは何ですか");

        Assert.Contains("問い合わせ中にエラー", response);
    }

    private static FoundryAgentChatService CreateService(IFoundryAgentClient client, FoundryAgentOptions options)
    {
        return new FoundryAgentChatService(
            client,
            new StubDashboardDataService(),
            Options.Create(options),
            NullLogger<FoundryAgentChatService>.Instance);
    }

    private static async Task<string> CollectResponseAsync(FoundryAgentChatService service, string message)
    {
        var chunks = new List<string>();
        await foreach (var chunk in service.SendMessageAsync("conv-1", message))
        {
            chunks.Add(chunk);
        }

        return string.Concat(chunks);
    }

    private sealed class StubFoundryAgentClient : IFoundryAgentClient
    {
        private readonly string _response;

        public StubFoundryAgentClient(string response)
        {
            _response = response;
        }

        public bool WasCalled { get; private set; }
        public string LastMessage { get; private set; } = string.Empty;

        public Task<string> SendMessageAsync(string conversationId, string message, CancellationToken cancellationToken = default)
        {
            WasCalled = true;
            LastMessage = message;
            return Task.FromResult(_response);
        }
    }

    private sealed class ThrowingFoundryAgentClient : IFoundryAgentClient
    {
        public Task<string> SendMessageAsync(string conversationId, string message, CancellationToken cancellationToken = default)
        {
            throw new InvalidOperationException("boom");
        }
    }

    private sealed class StubDashboardDataService : IDashboardDataService
    {
        public Task<DashboardSummary> GetDashboardSummaryAsync(CancellationToken cancellationToken = default)
        {
            return Task.FromResult(new DashboardSummary
            {
                TotalProjects = 2,
                ServiceCandidateCount = 1,
                TotalContractedSales = 100_000_000m,
                AverageProfitMargin = 0.25,
                AnalysisStatus = "completed",
                ServiceCandidates =
                [
                    new ServiceCandidate
                    {
                        CandidateId = "CAND-001",
                        Rank = 1,
                        Name = "候補A",
                        ExecutiveSummary = "経営向け要約",
                        Scores = new CandidateScores { Priority = 92 },
                        Metrics = new CandidateMetrics
                        {
                            SupportingProjectCount = 3,
                            WinRate = 0.75,
                            AverageMarginRate = 0.25
                        },
                        RecommendedBusinessModel = new RecommendedBusinessModel
                        {
                            Current = "Standard Offering",
                            Next = "Managed Service",
                            FutureOption = "SaaS"
                        }
                    }
                ]
            });
        }
    }
}
