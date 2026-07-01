---
documentId: DOC-P004-RETRO
projectId: P004
customerId: C002
title: P004 Retrospective - Contact Center Knowledge Agent
documentType: Retrospective
industry: Telecommunications
projectTheme: AI Agent Production
winLoss: Won
knowledgeStatus: Approved
confidentiality: Internal
sourceDate: 2024-12-15
tags:
  - retrospective
  - ai-agent
  - contact-center
  - telecommunications
  - escalation-rate
sourceUrl: https://demo.local/documents/P004/P004-retrospective
---

# P004 Retrospective - Contact Center Knowledge Agent

## 1. 背景

コンタクトセンターナレッジエージェントは2024年5月から12月にかけて開発・本番稼働を完了した。通信業界のコンプライアンス要件に対応しながら、ナレッジ検索効率と回答精度の大幅改善を実現した。

## 2. 顧客課題

ナレッジ検索の非効率・回答精度の不足・エスカレーション率の高さ・コンプライアンス記録義務という4課題を解決した。

## 3. 主要要件

6要件すべてを実装完了した。

## 4. 提案／実装内容

ACL-aware Retrieval・Citation and Grounding・Evaluation Pipeline・Human Escalation・CRMログ統合を実装した。

## 5. 主要リスクと対策

4リスクをすべてMitigatedとした。

## 6. 結果

| 指標 | 導入前 | 導入後 | 改善 |
|---|---:|---:|---:|
| ナレッジ検索時間 | 12分 | 4分 | -66.7% |
| 回答精度 | 68% | 84% | +23.5% |
| エスカレーション率 | 35% | 29% | -17.1% |

収益: 410百万円、利益: 90百万円（利益率22.0%）、工数削減率: 20%

## 7. 再利用可能な教訓

- **CRM統合の先行設計**: エスカレーションログのCRM統合は、コンプライアンス証跡として後から要求されることが多いため先行設計が有効
- **精度目標の事前合意**: 精度68%→84%という目標を本番前に合意していたため、KPI達成の確認が円滑だった
- **エスカレーション条件の可視化**: 転送条件のダッシュボード表示がオペレーターの業務改善フィードバック収集に役立った

## 8. 再利用時の注意

- 通信業界のコンプライアンス要件（ログ保持年数・アクセス記録範囲）は他業種と異なる場合がある
- 精度改善の速度はナレッジ品質と更新頻度に依存するため、目標設定時に現状のナレッジ品質を確認すること
