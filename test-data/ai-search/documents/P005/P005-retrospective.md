---
documentId: DOC-P005-RETRO
projectId: P005
customerId: C003
title: P005 Retrospective - Predictive Maintenance Data Platform
documentType: Retrospective
industry: Manufacturing
projectTheme: AI-ready Data Foundation
winLoss: Won
knowledgeStatus: Approved
confidentiality: Internal
sourceDate: 2024-09-30
tags:
  - retrospective
  - data-foundation
  - predictive-maintenance
  - manufacturing
  - downtime-reduction
sourceUrl: https://demo.local/documents/P005/P005-retrospective
---

# P005 Retrospective - Predictive Maintenance Data Platform

## 1. 背景

予知保全データプラットフォームは2024年1月から9月にかけて構築・本番稼働を完了した。複数工場のセンサーデータをFabric Lakehouseに統合し、Data Agentと Semantic Modelで分析環境を整備した。

## 2. 顧客課題

データ分散・異常検知遅延・分析準備時間・ダウンタイム損失という4課題を解決した。

## 3. 主要要件

6要件すべてを計画通りに実装完了した。

## 4. 提案／実装内容

Lakehouse・Data Pipelines・Semantic Model・Ontology・Data Agentの5機能を順次実装した。

## 5. 主要リスクと対策

ソース間不整合・データオーナー不明確・取り込み遅延・容量コスト増大の4リスクをすべてMitigatedとした。

## 6. 結果

| 指標 | 導入前 | 導入後 | 改善 |
|---|---:|---:|---:|
| 四半期ダウンタイム時間 | 18時間 | 11時間 | -38.9% |
| 異常検知時間 | 24時間 | 3時間 | -87.5% |
| 分析準備時間 | 8時間 | 2時間 | -75.0% |

収益: 600百万円、利益: 190百万円（利益率31.7%）、工数削減率: 35%

## 7. 再利用可能な教訓

- **データオーナー先行確定**: データオーナーの確定が移行着手の絶対条件であり、未確定のままの移行開始は後のガバナンス問題の原因となる
- **Ontology設計の工数**: 業務専門家との協議を含めたOntology設計は想定より時間がかかるため、プロジェクト計画に十分なバッファを確保すること
- **パイプライン品質チェック**: 取り込み時の品質チェックは後処理よりも大幅にコストが低く、データ信頼性への早期投資として効果的
- **5分取り込みと予知保全**: 5分間隔の準リアルタイム取り込みは、24時間対応の製造設備では十分な検知速度を提供できた

## 8. 再利用時の注意

- 製造業特有のIoTプロトコル（Modbus・OPC-UA等）はFabricへの取り込み前に変換レイヤーが必要な場合がある
- データ量（センサー台数・サンプリング頻度）によって容量設計とコスト試算を個別に実施すること
- 製造業以外ではOntology定義（設備・メンテナンス概念）を業種の業務概念に合わせて全面再設計すること
