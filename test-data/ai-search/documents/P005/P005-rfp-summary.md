---
documentId: DOC-P005-RFP
projectId: P005
customerId: C003
title: P005 RFP Summary - Predictive Maintenance Data Platform
documentType: RfpSummary
industry: Manufacturing
projectTheme: AI-ready Data Foundation
winLoss: Won
knowledgeStatus: Approved
confidentiality: Internal
sourceDate: 2023-12-10
tags:
  - data-foundation
  - lakehouse
  - predictive-maintenance
  - manufacturing
  - iot
sourceUrl: https://demo.local/documents/P005/P005-rfp-summary
---

# P005 RFP Summary - Predictive Maintenance Data Platform

## 1. 背景

製造業Customer Cでは複数工場の生産設備に多数のIoTセンサーを設置しているが、収集したデータが各工場の個別システムに分散しており、全社的な設備稼働分析ができていなかった。四半期ダウンタイムが18時間に達し、計画外停止による生産損失が経営課題となっていた。異常検知に最大24時間かかり、分析準備だけで8時間を要するデータ準備の非効率も問題だった。複数センサーデータを統合し、AIを活用した予知保全を可能にするデータ基盤の構築が求められた。

## 2. 顧客課題

- 複数工場のセンサーデータが分散しており全社設備分析ができない
- 異常検知に最大24時間かかり予防的対応が間に合わない
- データ準備に毎回8時間かかり分析チームの生産性が低い
- ダウンタイム18時間/四半期による生産損失が継続している
- データオーナーが工場ごとに分かれており統合のガバナンスが困難

## 3. 主要要件

| 要件 | 優先度 |
|---|---|
| 複数センサー統合Unified Data Model | High |
| データ品質チェックルールの自動適用 | High |
| センサーからモデルまでのData Lineage | High |
| 設備稼働指標のSemantic Model | High |
| Near-real-time センサーデータ取り込み | High |
| 工場・部門・職種ロール別RBAC | High |

## 4. 提案／実装内容

Microsoft Fabric Lakehouseを中核とした全社統合データ基盤を構築し、Data AgentとSemantic Modelで予知保全の分析環境を整備することを提案した。

## 5. 主要リスクと対策

- **ソース間不整合**: パイプライン内整合性チェックと自動アラート
- **データオーナー不明確**: 工場別データオーナーを確定してから移行
- **取り込み遅延**: SLAと遅延アラートの事前設定

## 6. 結果

提案は採択され、プロジェクトP005として受注した。

## 7. 再利用可能な教訓

- 製造業IoTデータはセンサーごとにスキーマが異なるため、Unified Data Modelの設計に各機器ベンダーとの技術協議が必要
- データオーナーの特定は移行計画策定の前提条件であり、特定できない場合は移行を開始しないことが重要

## 8. 再利用時の注意

- IoTセンサーの種類と数によって取り込みパイプラインの設計が大きく異なる
- 製造業特有の工場間ネットワーク制約がデータ転送に影響する場合がある
