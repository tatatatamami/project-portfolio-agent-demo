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
            TotalProjects = 12,
            ServiceCandidateCount = 3,
            TotalContractedSales = 4_780_000_000m,
            AverageProfitMargin = 28.1,
            ServiceCandidates =
            [
                new ServiceCandidate
                {
                    Name = "AIデータ活用基盤オファリング",
                    Rank = 1,
                    Priority = 100.0,
                    WinRate = 100.0,
                    AverageProfitMargin = 32.0,
                    AverageEffortReductionRate = 35.8,
                    IndustryCount = 4,
                    ReuseRatePct = 100.0,
                    TotalWonRevenueJPYBillion = 21.9,
                    RecommendedBusinessModel = "標準オファリング化 → SaaS化検証",
                    Rationale = "製造・小売・メディア・物流の4業種・4案件で、データパイプライン、Lakehouse、セマンティックモデル、Data Agentなどの共通構成が確認され、4案件すべてを受注しています。業種を越えて再利用できる可能性が高く、受注率100%・平均利益率32.0%は全パターン中最高であるため、最優先の事業化候補と判断しました。",
                    SupportingProjects = ["P005（製造）", "P007（小売）", "P009（メディア）", "P012（物流）"],
                    ReuseAssets =
                    [
                        "データパイプライン（4/4案件）",
                        "Lakehouse（4/4案件）",
                        "セマンティックモデル（4/4案件）",
                        "Data Agent（4/4案件）",
                        "データ品質・リネージ管理（4/4案件）",
                        "ロールベースアクセス制御（4/4案件）"
                    ],
                    RequiredPreparation =
                    [
                        "標準Discoveryテンプレート",
                        "標準リファレンスアーキテクチャ",
                        "データオーナーとRACIの定義",
                        "標準Lakehouse構成",
                        "導入・運用手順",
                        "価格・契約モデル",
                        "テナント分離方式",
                        "サポートレベル定義"
                    ],
                    AssetizationStageIndex = 2,
                    CommonRequirements = ["統合データモデル", "データ品質ルール", "データリネージ", "セマンティックモデル", "準リアルタイム取り込み", "ロールベースアクセス制御"],
                    MajorRisks = ["ソース間の不整合", "データオーナー不明確", "取り込み遅延", "容量・コスト増大"],
                    NextManagementDecision = "AIデータ活用基盤の標準提供範囲を決定し、次の2案件をパイロット対象として選定する。標準化設計・価格モデル・テナント分離方式の確定に投資判断が必要。"
                },
                new ServiceCandidate
                {
                    Name = "APIモダナイゼーション・アクセラレータ",
                    Rank = 2,
                    Priority = 81.8,
                    WinRate = 75.0,
                    AverageProfitMargin = 28.3,
                    AverageEffortReductionRate = 30.3,
                    IndustryCount = 3,
                    ReuseRatePct = 75.0,
                    TotalWonRevenueJPYBillion = 15.0,
                    RecommendedBusinessModel = "アクセラレータ＋マネージドサービス",
                    Rationale = "ゲーム・通信・物流の3業種・3案件（受注）でAPI Gateway、Entra ID認証、バージョン管理、分散オブザーバビリティの共通構成が確認されています。ERP連携案件（P006）の失注から、APIオーナーシップの先行確定がPoC成功の必要条件として判明しました。Discoveryフェーズの標準化により再現性を高められます。",
                    SupportingProjects = ["P001（Gaming）", "P003（通信）", "P006（製造・失注）", "P011（物流）"],
                    ReuseAssets =
                    [
                        "API Gateway構成（4/4案件）",
                        "Entra ID認証テンプレート（3/4案件）",
                        "レート制限ポリシー（4/4案件）",
                        "APIバージョン管理（4/4案件）",
                        "分散オブザーバビリティ（4/4案件）"
                    ],
                    RequiredPreparation =
                    [
                        "Discovery Phaseテンプレート",
                        "APIオーナー確定プロセス",
                        "非機能要件合意フレームワーク",
                        "ゼロダウンタイム移行手順書",
                        "パートナー通知プロセス"
                    ],
                    AssetizationStageIndex = 2,
                    CommonRequirements = ["Identity and Authentication", "Rate Limiting", "API Versioning", "Audit Logging", "Observability", "Zero-downtime Migration"],
                    MajorRisks = ["認証設定不備", "ピーク負荷", "Breaking Change", "APIオーナー不在"],
                    NextManagementDecision = "Discovery Phaseを標準先行ステップとして必須化し、APIオーナーの確定なしには技術提案を進めない方針を確立する。"
                },
                new ServiceCandidate
                {
                    Name = "AIエージェント本番化・運用プラットフォーム",
                    Rank = 3,
                    Priority = 70.7,
                    WinRate = 75.0,
                    AverageProfitMargin = 22.9,
                    AverageEffortReductionRate = 23.0,
                    IndustryCount = 3,
                    ReuseRatePct = 75.0,
                    TotalWonRevenueJPYBillion = 10.9,
                    RecommendedBusinessModel = "マネージドプラットフォーム → SaaS化検証",
                    Rationale = "ゲーム・通信・小売の3業種・3案件（受注）でACL対応検索、引用表示、評価パイプライン、人間エスカレーションの共通構成が確認されています。メディア案件（P010）の失注から、データ権限整理と受け入れ基準の事前合意がAIエージェント案件の必要条件として判明しました。",
                    SupportingProjects = ["P002（Gaming）", "P004（通信）", "P008（小売）", "P010（メディア・失注）"],
                    ReuseAssets =
                    [
                        "ACL対応グラウンデッド検索（3/4案件）",
                        "引用・根拠表示（4/4案件）",
                        "評価パイプライン（4/4案件）",
                        "Content Safety（4/4案件）",
                        "人間エスカレーション（4/4案件）"
                    ],
                    RequiredPreparation =
                    [
                        "AI Production Readiness Assessmentテンプレート",
                        "受け入れ基準合意フレームワーク",
                        "データ権限整理チェックリスト",
                        "本番運用責任定義書",
                        "評価指標標準セット"
                    ],
                    AssetizationStageIndex = 2,
                    CommonRequirements = ["Access Control / ACL Trimming", "Citation / Grounding", "Evaluation", "Content Safety", "Human Escalation", "Monitoring and Feedback"],
                    MajorRisks = ["Hallucination", "Data Oversharing", "Stale Knowledge", "Acceptance Criteria不明確"],
                    NextManagementDecision = "AI Production Readiness Assessmentを提案プロセスの必須ステップとして標準化し、本番移行計画の具体性を提案競争力の核とする。"
                }
            ]
        };

        return Task.FromResult(summary);
    }
}
