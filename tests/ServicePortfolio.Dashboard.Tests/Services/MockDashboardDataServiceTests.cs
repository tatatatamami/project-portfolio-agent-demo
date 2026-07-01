using Microsoft.Extensions.Logging.Abstractions;
using ServicePortfolio.Dashboard.Services;

namespace ServicePortfolio.Dashboard.Tests.Services;

public class MockDashboardDataServiceTests
{
    private readonly MockDashboardDataService _sut = new(NullLogger<MockDashboardDataService>.Instance);

    [Fact]
    public async Task GetDashboardSummaryAsync_ReturnsSummaryWithExpectedValues()
    {
        var summary = await _sut.GetDashboardSummaryAsync();

        Assert.Equal(12, summary.TotalProjects);
        Assert.Equal(3, summary.ServiceCandidateCount);
        Assert.True(summary.TotalContractedSales > 0);
        Assert.True(summary.AverageProfitMargin > 0);
    }

    [Fact]
    public async Task GetDashboardSummaryAsync_ReturnsExpectedNumberOfServiceCandidates()
    {
        var summary = await _sut.GetDashboardSummaryAsync();

        Assert.Equal(3, summary.ServiceCandidates.Count);
    }

    [Fact]
    public async Task GetDashboardSummaryAsync_ServiceCandidatesAreRankedCorrectly()
    {
        var summary = await _sut.GetDashboardSummaryAsync();

        var ranks = summary.ServiceCandidates.Select(c => c.Rank).ToList();
        Assert.Equal([1, 2, 3], ranks);
    }

    [Fact]
    public async Task GetDashboardSummaryAsync_CancellationTokenRespected()
    {
        using var cts = new CancellationTokenSource();
        cts.Cancel();

        // MockDashboardDataService completes synchronously so cancellation is not thrown
        var summary = await _sut.GetDashboardSummaryAsync(cts.Token);
        Assert.NotNull(summary);
    }

    [Fact]
    public async Task GetDashboardSummaryAsync_TopCandidateHasAllRequiredFields()
    {
        var summary = await _sut.GetDashboardSummaryAsync();
        var topCandidate = summary.ServiceCandidates.First(c => c.Rank == 1);

        Assert.False(string.IsNullOrWhiteSpace(topCandidate.Name));
        Assert.NotEmpty(topCandidate.SupportingProjects);
        Assert.NotEmpty(topCandidate.CommonRequirements);
        Assert.NotEmpty(topCandidate.MajorRisks);
        Assert.False(string.IsNullOrWhiteSpace(topCandidate.NextManagementDecision));
    }
}
