---
documentId: DOC-P008-SOL
projectId: P008
customerId: C004
title: P008 Solution Summary - Store Operations AI Assistant
documentType: SolutionSummary
industry: Retail
projectTheme: AI Agent Production
winLoss: Won
knowledgeStatus: Approved
confidentiality: Internal
sourceDate: 2024-07-01
tags:
  - store-operations
  - acl-aware-retrieval
  - compliance
  - retail
  - human-escalation
sourceUrl: https://demo.local/documents/P008/P008-solution-summary
---

# P008 Solution Summary - Store Operations AI Assistant

## 1. 背景

店舗スタッフの業務効率化とコンプライアンス遵守の自動化のため、ACL対応の店舗業務AIアシスタントを構築した。

## 2. 顧客課題

業務完了40分・情報検索15分・コンプライアンス漏れ・手動ACL管理・ナレッジ陳腐化という5課題を解決した。

## 3. 主要要件

6要件すべてを実装完了した。

## 4. 提案／実装内容

**ACL-aware Retrieval**: 店舗スタッフのEntra IDトークンに含まれる職種（フロアスタッフ・チーフ・マネージャー）と担当エリア（売場・バックヤード・受発注）を検索クエリに適用し、権限外の価格交渉情報や機密在庫データを自動除外した。

**Citation and Grounding**: 商品情報・作業手順・コンプライアンス規則の回答にドキュメント名とセクション番号の引用を表示した。引用のない回答はエスカレーションに転送する設計とした。

**Content Safety**: 小売規制（景品表示法・個人情報保護）に関連する法的リスクのある表現を自動検出するカスタムセーフティルールを追加した。

**Evaluation Pipeline**: 週次で回答サンプルを評価し、コンプライアンス適切率・情報精度・引用有効性の3指標を追跡した。ナレッジ更新後に品質確認テストを自動実行した。

**Human Escalation**: 在庫不足・設備障害・クレーム対応・緊急安全事項の4カテゴリで店舗マネージャーへ自動転送した。

## 5. 主要リスクと対策

4リスクをすべてMitigatedとした。ナレッジ更新の自動化が品質維持の核心となった。

## 6. 結果

業務完了40分→26分、情報検索15分→5分、コンプライアンス遵守漏れ指数100→70を達成した。

## 7. 再利用可能な教訓

- **コンプライアンスルールのカスタマイズ**: 業種規制に対応したContent Safetyカスタムルールは、汎用ルールより大幅に精度が高く小売業の固有リスクに対応できた
- **職種×エリアのACL設計**: 職種だけでなく担当エリアを組み合わせたACL設計が、小売業のACL要件をより正確に反映できた
- **ナレッジ更新後テストの自動化**: 商品情報更新のたびに自動テストを実行することで、更新による品質劣化を即時検知できた

## 8. 再利用時の注意

- 小売規制（景品表示法・食品表示法等）は業種・商品カテゴリによって異なるため、Content Safetyルールは専門家とレビューすること
- 店舗数が多い場合はロール数×エリア数のACLマトリクスが大規模になるため、グループ化と抽象化が必要
