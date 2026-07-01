---
documentId: DOC-P009-RFP
projectId: P009
customerId: C005
title: P009 RFP Summary - Content Metadata Knowledge Platform
documentType: RfpSummary
industry: Media
projectTheme: AI-ready Data Foundation
winLoss: Won
knowledgeStatus: Approved
confidentiality: Internal
sourceDate: 2024-02-15
tags:
  - data-foundation
  - metadata-management
  - media
  - content-reuse
  - lakehouse
sourceUrl: https://demo.local/documents/P009/P009-rfp-summary
---

# P009 RFP Summary - Content Metadata Knowledge Platform

## 1. 背景

メディア事業者Customer Eでは映像・音楽・テキストコンテンツの制作・配信・アーカイブが複数のシステムで管理されており、コンテンツメタデータの統一基盤が存在しなかった。メタデータの完全性が62%にとどまり、既存コンテンツの検索に1件あたり平均20分かかる状態が続いていた。コンテンツ再利用率も12%と低く、制作コストと収益化機会の両面で損失が発生していた。AI活用を見据えたメタデータ統合基盤の構築が求められた。

## 2. 顧客課題

- コンテンツメタデータの完全性が62%と低く、AI活用の前提条件を満たしていない
- コンテンツ検索に平均20分かかり、制作チームの効率が低い
- 再利用可能な既存コンテンツの発見が困難なため、再制作コストが積み上がっている
- 制作・配信・アーカイブシステムのメタデータ形式が統一されておらず集計ができない
- コンテンツのライフサイクルが追跡できないため著作権管理と配信ルール整合性に問題がある

## 3. 主要要件

| 要件 | 優先度 |
|---|---|
| 複数ソースのコンテンツメタデータUnified Data Model | High |
| メタデータ品質の自動検証Data Quality Rules | High |
| コンテンツライフサイクルのData Lineage | High |
| 再利用・検索・収益指標のSemantic Model | High |
| 制作システムからのNear-real-time Ingestion | High |
| 制作・配信・経営層のRBAC | High |

## 4. 提案／実装内容

Microsoft Fabric LakehouseにコンテンツメタデータをAI活用可能な形で統合し、Data Agentで制作チームが自然言語でコンテンツを発見・分析できる環境を構築することを提案した。

## 5. 主要リスクと対策

- **ソース間不整合**: 制作・配信・アーカイブ間の変換ルールをパイプラインに組み込む
- **スキーマ進化**: 配信プラットフォームの仕様変更に対応したスキーマバージョン管理を導入

## 6. 結果

提案は採択され、プロジェクトP009として受注した。

## 7. 再利用可能な教訓

- メディア業界では著作権とライセンスのData Lineageが法的コンプライアンスの要件であり、単なる技術要件を超えた重要性を持つ
- メタデータ完全性の改善は検索精度だけでなくAIモデルの学習品質に直結するため、ROI説明がしやすい

## 8. 再利用時の注意

- メディア業界のメタデータ標準（Dublin Core・EBUCore等）は他業種には存在しないため、業種固有の標準化要件を確認すること
- コンテンツの権利関係は複雑なため、Data Lineageの設計に法務部門の参加が必要
