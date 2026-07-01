using Microsoft.Extensions.Logging;
using ServicePortfolio.Dashboard.Models;

namespace ServicePortfolio.Dashboard.Services;

public sealed class MockDashboardDataService : IDashboardDataService
{
    private readonly ILogger<MockDashboardDataService> _logger;

    public MockDashboardDataService(ILogger<MockDashboardDataService> logger)
    {
        _logger = logger;
    }

    public Task<DashboardSummary> GetDashboardSummaryAsync(CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Returning mock dashboard summary");

        var summary = new DashboardSummary
        {
            TotalProjects = 42,
            ServiceCandidateCount = 5,
            TotalContractedSales = 1_250_000_000m,
            AverageProfitMargin = 28.4,
            ServiceCandidates =
            [
                new ServiceCandidate
                {
                    Name = "クラウド移行支援サービス",
                    Rank = 1,
                    WinRate = 72.5,
                    AverageProfitMargin = 35.2,
                    AverageEffortReductionRate = 40.0,
                    SupportingProjects = ["案件A-12", "案件B-07", "案件C-23", "案件D-05"],
                    CommonRequirements = ["AWS/Azure対応", "セキュリティ要件", "移行計画策定", "運用支援"],
                    MajorRisks = ["既存システムとの互換性", "データ移行リスク", "運用スキル不足"],
                    NextManagementDecision = "パートナー企業との提携を通じて移行支援の専門チームを2ヶ月以内に編成し、標準化されたサービスメニューを策定する"
                },
                new ServiceCandidate
                {
                    Name = "AIデータ分析基盤構築",
                    Rank = 2,
                    WinRate = 58.3,
                    AverageProfitMargin = 42.1,
                    AverageEffortReductionRate = 55.0,
                    SupportingProjects = ["案件E-31", "案件F-18", "案件G-09"],
                    CommonRequirements = ["データパイプライン", "機械学習モデル", "ダッシュボード", "API連携"],
                    MajorRisks = ["データ品質・ガバナンス", "AI規制対応", "人材確保の困難"],
                    NextManagementDecision = "データサイエンティスト採用計画を策定し、既存エンジニアへのAI研修プログラムを開始する"
                },
                new ServiceCandidate
                {
                    Name = "業務プロセス自動化（RPA+AI）",
                    Rank = 3,
                    WinRate = 65.0,
                    AverageProfitMargin = 30.8,
                    AverageEffortReductionRate = 62.0,
                    SupportingProjects = ["案件H-44", "案件I-22"],
                    CommonRequirements = ["RPA導入", "プロセス分析", "例外処理設計", "保守体制"],
                    MajorRisks = ["業務変更への抵抗", "ROI測定の複雑さ"],
                    NextManagementDecision = "RPA専門チームを社内に設立し、パイロット案件で標準化を推進する"
                },
                new ServiceCandidate
                {
                    Name = "セキュリティ監査・対策支援",
                    Rank = 4,
                    WinRate = 45.0,
                    AverageProfitMargin = 38.5,
                    AverageEffortReductionRate = 25.0,
                    SupportingProjects = ["案件J-11", "案件K-33"],
                    CommonRequirements = ["脆弱性診断", "ISMS対応", "インシデント対応", "教育研修"],
                    MajorRisks = ["法改正への追随", "専門人材の育成コスト"],
                    NextManagementDecision = "セキュリティ資格保有者の採用を優先し、セキュリティサービス部門を立ち上げる"
                },
                new ServiceCandidate
                {
                    Name = "デジタル人材育成研修",
                    Rank = 5,
                    WinRate = 80.0,
                    AverageProfitMargin = 22.0,
                    AverageEffortReductionRate = 15.0,
                    SupportingProjects = ["案件L-02", "案件M-19", "案件N-28"],
                    CommonRequirements = ["カリキュラム設計", "ハンズオン環境", "評価システム", "継続支援"],
                    MajorRisks = ["受講者スキルのばらつき", "研修効果の持続性"],
                    NextManagementDecision = "オンライン研修プラットフォームを導入し、顧客の内製化支援メニューを拡充する"
                }
            ]
        };

        return Task.FromResult(summary);
    }
}
