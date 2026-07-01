---
documentId: DOC-P004-SOL
projectId: P004
customerId: C002
title: P004 Solution Summary - Contact Center Knowledge Agent
documentType: SolutionSummary
industry: Telecommunications
projectTheme: AI Agent Production
winLoss: Won
knowledgeStatus: Approved
confidentiality: Internal
sourceDate: 2024-06-01
tags:
  - knowledge-agent
  - acl-aware-retrieval
  - evaluation-pipeline
  - telecommunications
  - compliance
sourceUrl: https://demo.local/documents/P004/P004-solution-summary
---

# P004 Solution Summary - Contact Center Knowledge Agent

## 1. 背景

コンタクトセンターのナレッジ検索効率化と回答精度向上を目的に、ACL制御を中核としたナレッジエージェントを構築した。

## 2. 顧客課題

ナレッジ検索12分・精度68%・エスカレーション率35%・コンプライアンスログ義務という4課題を解決した。

## 3. 主要要件

6要件すべてを実装完了した。

## 4. 提案／実装内容

**ACL-aware Retrieval**: オペレーターのEntra IDトークンに含まれるロール（一般・シニア・スーパーバイザー）を検索クエリに適用し、権限外の顧客情報や機密手順書を検索結果から除外した。

**Citation and Grounding**: 全回答に社内ナレッジの文書タイトルとセクション引用を表示し、オペレーターが顧客への案内前に根拠を確認できる設計とした。引用がない回答は自動エスカレーションに転送した。

**Evaluation Pipeline**: 月次で回答サンプルを自動評価し、精度・引用有効性・Content Safety合格率・エスカレーション適切率の4指標を追跡した。低下検知時はナレッジ更新とモデル調整サイクルを実行した。

**Human Escalation**: 苦情・未解決3回以上・法的リスクキーワードの3条件でスーパーバイザーへ自動転送した。転送履歴はCRMログに記録しコンプライアンス対応に活用した。

## 5. 主要リスクと対策

4リスクすべてをMitigatedとした。コンプライアンスログはCRM統合で自動記録を実現した。

## 6. 結果

ナレッジ検索12分→4分、回答精度68%→84%、エスカレーション率35%→29%を達成した。

## 7. 再利用可能な教訓

- コンタクトセンターではエスカレーションログのCRM統合がコンプライアンス証跡として活用できる
- 月次評価でなく週次にすることで品質劣化の検知が2倍速くなる
- 引用表示はオペレーターの顧客への説明品質を向上させる副次効果がある

## 8. 再利用時の注意

- ロール数が多い場合（10種以上）はACL設計にロールグループの概念を導入して複雑性を管理すること
- コンタクトセンター特有のシフト管理とロール切り替えに動的な権限反映が必要
