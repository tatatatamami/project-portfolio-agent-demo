using ServicePortfolio.Dashboard.Models;

namespace ServicePortfolio.Dashboard.Services;

public interface IDashboardDataService
{
    Task<DashboardSummary> GetDashboardSummaryAsync(CancellationToken cancellationToken = default);
}
