using System.Runtime.CompilerServices;
using Microsoft.Extensions.Logging;

namespace ServicePortfolio.Dashboard.Services;

public sealed class FakeAgentChatService : IAgentChatService
{
    private readonly ILogger<FakeAgentChatService> _logger;

    private static readonly Dictionary<string, string> _responses = new(StringComparer.OrdinalIgnoreCase)
    {
        ["根拠"] = """
            ## クラウド移行支援サービスを優先する根拠

            以下の分析に基づいています。

            ### 定量的根拠
            - **受注率 72.5%**: 他のサービス候補と比較して最も高い受注率
            - **平均工数削減率 40%**: 顧客の運用負荷を大幅に軽減
            - **根拠案件数 4件**: 複数の成功事例が存在

            ### 市場動向
            クラウド移行需要は今後3〜5年で急拡大が見込まれます。競合他社が本格参入する前に市場ポジションを確立することが重要です。

            ### 推奨アクション
            1. 専門チームの編成（2ヶ月以内）
            2. 標準サービスメニューの策定
            3. パイロット顧客との契約締結
            """,

        ["成功"] = """
            ## 成功案件と失注案件の違い

            ### 成功案件の特徴
            | 要素 | 詳細 |
            |------|------|
            | 提案タイミング | 顧客の課題認識直後 |
            | 対応速度 | 初回提案まで平均3営業日 |
            | 提案内容 | ROI明示・段階的移行計画 |
            | 関係者 | CTO・IT部門長が意思決定に参加 |

            ### 失注案件の主な原因
            1. **価格競争**: 単純な価格比較で負けたケース（全失注の35%）
            2. **提案の遅延**: 競合他社より提案が遅かったケース（28%）
            3. **要件理解不足**: 顧客の業務要件を十分に把握できなかったケース（22%）

            ### 改善ポイント
            - 早期ヒアリングの仕組み化
            - 価値訴求型の提案書テンプレート整備
            """,

        ["リスク"] = """
            ## サービス化前に確認すべきリスク

            ### 技術リスク
            - **既存システム互換性**: レガシーシステムとの統合複雑性
            - **データ移行品質**: 移行データの整合性確認プロセス
            - **セキュリティ要件**: クラウド環境でのコンプライアンス対応

            ### ビジネスリスク
            - **人材リスク**: 専門エンジニアの確保・育成（6〜12ヶ月のリードタイム）
            - **パートナー依存**: ベンダー契約条件の見直し必要性
            - **価格設定**: 競合他社との価格差別化戦略

            ### 組織リスク
            - 既存事業との利益相反
            - 社内スキルトランスファーの計画

            ### 推奨する確認事項
            1. 技術デューデリジェンスの実施
            2. 法務・コンプライアンスチェック
            3. 財務シミュレーション（3年間）
            """,

        ["経営アクション"] = """
            ## 次の経営アクション（優先度順）

            ### アクション1: 専門チーム編成（〜2ヶ月）
            クラウド移行支援の専門チームを編成します。
            - 対象: 社内エンジニア3〜5名 + 外部パートナー
            - 予算: 人件費 + 研修費用
            - KPI: チーム編成完了・資格取得者数

            ### アクション2: サービスメニュー標準化（〜3ヶ月）
            再現性のあるサービスパッケージを策定します。
            - 成果物: サービス仕様書・見積もりテンプレート・契約書雛形
            - 担当: プロジェクトマネージャー + 営業

            ### アクション3: パイロット顧客獲得（〜4ヶ月）
            既存顧客から2〜3社をパイロットとして選定します。
            - 選定基準: クラウド移行意向あり・予算承認済み
            - 目標: サービス品質の検証と事例作成
            """
    };

    public FakeAgentChatService(ILogger<FakeAgentChatService> logger)
    {
        _logger = logger;
    }

    public string CreateConversationId() => Guid.NewGuid().ToString("N");

    public async IAsyncEnumerable<string> SendMessageAsync(
        string conversationId,
        string message,
        [EnumeratorCancellation] CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("FakeAgent processing message in conversation {ConversationId}", conversationId);

        var response = SelectResponse(message);
        var words = response.Split(' ');

        foreach (var word in words)
        {
            cancellationToken.ThrowIfCancellationRequested();
            await Task.Delay(30, cancellationToken);
            yield return word + " ";
        }
    }

    private static string SelectResponse(string message)
    {
        foreach (var (key, response) in _responses)
        {
            if (message.Contains(key, StringComparison.OrdinalIgnoreCase))
                return response;
        }

        return """
            ## ご質問について

            ご質問ありがとうございます。

            現在、このデモでは以下のトピックについて詳細な情報を提供できます。

            - **優先根拠**: サービス候補を優先する定量的・定性的根拠
            - **成功/失注分析**: 案件の成否要因の比較
            - **リスク評価**: サービス化前に確認すべきリスク一覧
            - **経営アクション**: 次に取るべき具体的なアクション

            上記の質問候補からお選びいただくか、関連するキーワードを含めてご質問ください。
            """;
    }
}
