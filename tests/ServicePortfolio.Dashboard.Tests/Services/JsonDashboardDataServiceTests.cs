using Microsoft.AspNetCore.Hosting;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.FileProviders;
using Microsoft.Extensions.Logging.Abstractions;
using ServicePortfolio.Dashboard.Services;

namespace ServicePortfolio.Dashboard.Tests.Services;

public sealed class JsonDashboardDataServiceTests
{
    [Fact]
    public async Task GetDashboardSummaryAsync_LoadsGeneratedDashboardData()
    {
        var service = CreateService(FindRepoRoot());

        var summary = await service.GetDashboardSummaryAsync();

        Assert.False(summary.HasError);
        Assert.Equal(12, summary.TotalProjects);
        Assert.Equal(3, summary.ServiceCandidateCount);
        Assert.Equal(4_780_000_000m, summary.TotalContractedSales);
        Assert.Equal(28.1, summary.AverageProfitMargin);
        Assert.Contains(summary.ModelProvider, new[] { "dry-run", "azure-openai" });
        Assert.False(string.IsNullOrWhiteSpace(summary.ModelDeployment));
    }

    [Fact]
    public async Task GetDashboardSummaryAsync_ReturnsCandidatesInRankOrder()
    {
        var service = CreateService(FindRepoRoot());

        var summary = await service.GetDashboardSummaryAsync();

        Assert.Equal([1, 2, 3], summary.ServiceCandidates.Select(candidate => candidate.Rank).ToArray());
        Assert.Equal("CAND-001", summary.ServiceCandidates[0].CandidateId);
        Assert.Equal(77, summary.ServiceCandidates[0].Scores.Priority);
        Assert.Equal(77, summary.ServiceCandidates[0].Ice?.Score);
    }

    [Fact]
    public async Task GetDashboardSummaryAsync_MapsCandidateDetails()
    {
        var service = CreateService(FindRepoRoot());

        var summary = await service.GetDashboardSummaryAsync();
        var topCandidate = summary.ServiceCandidates.First();

        Assert.NotEmpty(topCandidate.ExecutiveSummary);
        Assert.NotEmpty(topCandidate.BusinessReason);
        Assert.NotEmpty(topCandidate.SupportingProjects);
        Assert.NotEmpty(topCandidate.ReusableAssets);
        Assert.NotEmpty(topCandidate.StandardizationGaps);
        Assert.NotEmpty(topCandidate.Risks);
        Assert.NotEmpty(topCandidate.ManagementDecision.Next90Days);
        Assert.NotEmpty(topCandidate.BusinessReasonSourceIds);
        Assert.NotEmpty(topCandidate.StandardizationGaps[0].SourceIds);
        Assert.NotEmpty(topCandidate.ManagementDecision.Next90Days[0].SourceIds);
        Assert.Equal(topCandidate.Scores.Priority, topCandidate.Ice?.Score);
        Assert.NotEmpty(topCandidate.Ice?.Impact.Factors ?? []);
        Assert.Contains(topCandidate.Ice?.Impact.Factors ?? [], factor => factor.Name == "受注率" && factor.Value == "100.0%");
    }

    [Fact]
    public async Task GetDashboardSummaryAsync_ReturnsErrorSummaryWhenJsonIsMissing()
    {
        using var tempDirectory = new TempDirectory();
        var configuration = new ConfigurationBuilder()
            .AddInMemoryCollection(new Dictionary<string, string?>
            {
                ["DashboardData:Path"] = "missing-dashboard-data.json"
            })
            .Build();
        var service = new JsonDashboardDataService(
            new TestWebHostEnvironment(tempDirectory.Path),
            configuration,
            NullLogger<JsonDashboardDataService>.Instance);

        var summary = await service.GetDashboardSummaryAsync();

        Assert.True(summary.HasError);
        Assert.False(summary.HasAnalysisResults);
        Assert.Contains("分析結果ファイルが見つかりません", summary.ErrorMessage);
    }

    private static JsonDashboardDataService CreateService(string repoRoot)
    {
        var configuration = new ConfigurationBuilder()
            .AddInMemoryCollection(new Dictionary<string, string?>
            {
                ["DashboardData:Path"] = "../../analysis/output/dashboard-data.json"
            })
            .Build();

        return new JsonDashboardDataService(
            new TestWebHostEnvironment(Path.Combine(repoRoot, "src", "ServicePortfolio.Dashboard")),
            configuration,
            NullLogger<JsonDashboardDataService>.Instance);
    }

    private static string FindRepoRoot()
    {
        var directory = new DirectoryInfo(AppContext.BaseDirectory);
        while (directory is not null)
        {
            if (File.Exists(Path.Combine(directory.FullName, "analysis", "output", "dashboard-data.json")))
                return directory.FullName;

            directory = directory.Parent;
        }

        throw new InvalidOperationException("Repository root could not be found.");
    }

    private sealed class TestWebHostEnvironment : IWebHostEnvironment
    {
        public TestWebHostEnvironment(string contentRootPath)
        {
            ContentRootPath = contentRootPath;
            WebRootPath = contentRootPath;
            ContentRootFileProvider = new PhysicalFileProvider(contentRootPath);
            WebRootFileProvider = new PhysicalFileProvider(contentRootPath);
        }

        public string ApplicationName { get; set; } = "ServicePortfolio.Dashboard.Tests";
        public IFileProvider ContentRootFileProvider { get; set; }
        public string ContentRootPath { get; set; }
        public string EnvironmentName { get; set; } = "Development";
        public string WebRootPath { get; set; }
        public IFileProvider WebRootFileProvider { get; set; }
    }

    private sealed class TempDirectory : IDisposable
    {
        public TempDirectory()
        {
            Path = System.IO.Path.Combine(System.IO.Path.GetTempPath(), Guid.NewGuid().ToString("N"));
            Directory.CreateDirectory(Path);
        }

        public string Path { get; }

        public void Dispose()
        {
            if (Directory.Exists(Path))
                Directory.Delete(Path, recursive: true);
        }
    }
}