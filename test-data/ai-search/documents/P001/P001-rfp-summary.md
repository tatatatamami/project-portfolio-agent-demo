---
documentId: DOC-P001-RFP
projectId: P001
customerId: C001
title: P001 RFP Summary - Game LiveOps API Modernization
documentType: RfpSummary
industry: Gaming
projectTheme: API Modernization
winLoss: Won
knowledgeStatus: Approved
confidentiality: Internal
sourceDate: 2023-12-15
tags:
  - api-modernization
  - authentication
  - rate-limiting
  - observability
  - gaming
sourceUrl: https://demo.local/documents/P001/P001-rfp-summary
---

# P001 RFP Summary - Game LiveOps API Modernization

## 1. 背景

ゲーム事業会社Customer Aでは、タイトルのグローバル展開に伴いLiveOpsパートナーが急増し、外部APIへのリクエスト量が年間で3倍以上に膨れ上がっていた。既存のAPIはモノリシックな構成で認証機能も各チームが個別実装しており、セキュリティポリシーの統一が困難な状態であった。加えてLiveOpsイベント期間中のトラフィック集中によって本番環境で断続的なタイムアウトが発生しており、パートナー連携の信頼性に深刻な影響を与えていた。この状況を根本的に解決するため、APIゲートウェイを中心とした近代化の提案要求が出された。

## 2. 顧客課題

- パートナーごとに異なる認証実装が乱立し、セキュリティレビューが困難になっている
- LiveOpsイベント時のトラフィック急増でAPIが断続的にタイムアウトし、パートナーからのクレームが増加している
- API仕様の変更が既存パートナーの連携システムに予告なく影響し、オンボーディングに平均20日を要している
- 障害発生時の原因特定に時間がかかり、インシデント対応コストが高止まりしている
- APIの変更管理プロセスが整備されておらず、デプロイ頻度が月2回に制限されている

## 3. 主要要件

| 要件 | 優先度 |
|---|---|
| Microsoft Entra IDによるOAuth 2.0認証の統一適用 | High |
| クライアント別レート制限によるAPIサービス保護 | High |
| URLパスバージョニングによる後方互換性維持 | High |
| 全APIリクエストの監査ログ記録 | Medium |
| 分散トレーシングとメトリクスによるリアルタイム監視 | High |
| ゼロダウンタイムでの段階的API移行 | High |

## 4. 提案／実装内容

本提案では、Azure API Managementをゲートウェイとして設置し、Microsoft Entra ID認証・レート制限・APIバージョン管理を統合する方針を示した。段階移行計画では既存パートナーの接続を維持しながら新APIへ切り替える方式を採用し、サービス断のリスクを最小化するアプローチを提案した。

## 5. 主要リスクと対策

- **認証設定不備**: Entra IDの設定を独立レビューとペネトレーションテストで検証する
- **ピーク負荷**: 事前負荷試験と自動スケーリングポリシーで過負荷を防止する
- **APIオーナー不明確**: 変更承認プロセスと連絡体制を文書化してからリリースする

## 6. 結果

提案は採択され、プロジェクトP001として受注に至った。

## 7. 再利用可能な教訓

- ゲーム業界ではLiveOpsイベントによるトラフィックスパイクをAPI設計の前提条件として組み込む必要がある
- 認証統一化はセキュリティだけでなくオンボーディング工数削減にも大きく貢献する
- パートナー向けAPIでは段階移行計画を提案段階で具体的に示すことが受注の鍵となる

## 8. 再利用時の注意

- レート制限の数値はトラフィックプロファイルを事前調査してから設定すること
- ゲーム以外の業界ではトラフィックパターンが異なるため、ピーク負荷の前提を再設定すること
- Entra ID設定はサービスの本番運用開始前に必ずペネトレーションテストで検証すること
