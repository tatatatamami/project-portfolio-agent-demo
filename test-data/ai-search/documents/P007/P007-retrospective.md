---
documentId: DOC-P007-RETRO
projectId: P007
customerId: C004
title: P007 Retrospective - Retail Demand Forecast Platform
documentType: Retrospective
industry: Retail
projectTheme: AI-ready Data Foundation
winLoss: Won
knowledgeStatus: Approved
confidentiality: Internal
sourceDate: 2024-11-30
tags:
  - retrospective
  - data-foundation
  - demand-forecasting
  - retail
  - stockout-reduction
sourceUrl: https://demo.local/documents/P007/P007-retrospective
---

# P007 Retrospective - Retail Demand Forecast Platform

## 1. 背景

小売需要予測プラットフォームは2024年2月から11月にかけて開発・本番稼働を完了した。全国POSデータをFabric Lakehouseに統合し、30分間隔の準リアルタイム取り込みと AI需要予測環境を実現した。

## 2. 顧客課題

予測誤差・データ鮮度・計画サイクル・複数POS統合・在庫プロモーション分断という5課題を解決した。

## 3. 主要要件

6要件すべてを計画通りに実装完了した。

## 4. 提案／実装内容

Lakehouse・Data Pipelines・Semantic Model・Ontology・Data Agentの5機能を実装した。

## 5. 主要リスクと対策

4リスクをすべてMitigatedとした。

## 6. 結果

| 指標 | 導入前 | 導入後 | 改善 |
|---|---:|---:|---:|
| 需要予測誤差率 | 28% | 18% | -35.7% |
| 欠品指数 | 100 | 85 | -15.0% |
| 計画サイクル | 3日 | 1日 | -66.7% |

収益: 560百万円、利益: 180百万円（利益率32.1%）、工数削減率: 38%

## 7. 再利用可能な教訓

- **商品コード名寄せを先行実施**: 複数POSシステムの商品コード統一はETL工数の40%を占めた。次回は名寄せを先行タスクとしてスコープに明示する
- **Ontologyのプロモーション定義**: プロモーション期間・種別をOntologyに明示的に定義することで、Data AgentのイベントQ&A精度が顕著に向上した
- **バイヤー向けUIの先行検証**: バイヤーがData Agentをどう使うかの仮説をPoC段階で検証しておくと、Ontology設計の方向性が明確になる

## 8. 再利用時の注意

- 小売業の需要予測は季節性が強いため、学習データの最低期間（2〜3年）を事前に確認すること
- 欠品率削減の定量効果は商品カテゴリと地域によって大きく異なるため、KPIは代表カテゴリで試算すること
