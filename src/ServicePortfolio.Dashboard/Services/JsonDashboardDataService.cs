using System.Text.Json;
using ServicePortfolio.Dashboard.Models;

namespace ServicePortfolio.Dashboard.Services;

public sealed class JsonDashboardDataService : IDashboardDataService
{
    private static readonly JsonSerializerOptions _jsonOptions = new(JsonSerializerDefaults.Web)
    {
        PropertyNameCaseInsensitive = true
    };

    private readonly IWebHostEnvironment _environment;
    private readonly IConfiguration _configuration;
    private readonly ILogger<JsonDashboardDataService> _logger;

    public JsonDashboardDataService(
        IWebHostEnvironment environment,
        IConfiguration configuration,
        ILogger<JsonDashboardDataService> logger)
    {
        _environment = environment;
        _configuration = configuration;
        _logger = logger;
    }

    public async Task<DashboardSummary> GetDashboardSummaryAsync(CancellationToken cancellationToken = default)
    {
        var dataPath = ResolveDashboardDataPath();
        if (!File.Exists(dataPath))
        {
            _logger.LogWarning("Dashboard data file was not found: {DataPath}", dataPath);
            return CreateErrorSummary($"分析結果ファイルが見つかりません: {dataPath}");
        }

        try
        {
            await using var stream = File.OpenRead(dataPath);
            var analysisData = await JsonSerializer.DeserializeAsync<PortfolioAnalysisData>(stream, _jsonOptions, cancellationToken);
            if (analysisData is null)
                return CreateErrorSummary("分析結果JSONを読み込めませんでした。");

            var candidates = analysisData.Candidates
                .OrderBy(candidate => candidate.Rank)
                .ToArray();

            return new DashboardSummary
            {
                TotalProjects = analysisData.DashboardSummary.ProjectCount,
                ServiceCandidateCount = analysisData.DashboardSummary.CandidateCount,
                TotalContractedSales = analysisData.DashboardSummary.WonRevenue,
                AverageProfitMargin = analysisData.DashboardSummary.AverageMarginRate,
                GeneratedAt = analysisData.AnalysisRun.GeneratedAt,
                ModelProvider = analysisData.AnalysisRun.ModelProvider,
                ModelDeployment = analysisData.AnalysisRun.ModelDeployment,
                AnalysisStatus = analysisData.AnalysisRun.Status,
                ServiceCandidates = candidates
            };
        }
        catch (JsonException ex)
        {
            _logger.LogError(ex, "Dashboard data JSON is invalid: {DataPath}", dataPath);
            return CreateErrorSummary($"分析結果JSONの形式が不正です: {ex.Message}");
        }
        catch (IOException ex)
        {
            _logger.LogError(ex, "Dashboard data file could not be read: {DataPath}", dataPath);
            return CreateErrorSummary($"分析結果ファイルを読み込めません: {ex.Message}");
        }
    }

    private string ResolveDashboardDataPath()
    {
        var configuredPath = _configuration["DashboardData:Path"];
        var relativeOrAbsolutePath = string.IsNullOrWhiteSpace(configuredPath)
            ? Path.Combine("..", "..", "analysis", "output", "dashboard-data.json")
            : configuredPath;

        return Path.GetFullPath(Path.IsPathRooted(relativeOrAbsolutePath)
            ? relativeOrAbsolutePath
            : Path.Combine(_environment.ContentRootPath, relativeOrAbsolutePath));
    }

    private static DashboardSummary CreateErrorSummary(string message) => new()
    {
        AnalysisStatus = "error",
        ErrorMessage = message,
        ServiceCandidates = []
    };
}