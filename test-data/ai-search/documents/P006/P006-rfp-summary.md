---
documentId: DOC-P006-RFP
projectId: P006
customerId: C003
title: P006 RFP Summary - ERP Integration Modernization
documentType: RfpSummary
industry: Manufacturing
projectTheme: API Modernization
winLoss: Lost
knowledgeStatus: Approved
confidentiality: Internal
sourceDate: 2024-02-01
tags:
  - api-modernization
  - erp-integration
  - manufacturing
  - authentication
  - lost
sourceUrl: https://demo.local/documents/P006/P006-rfp-summary
---

# P006 RFP Summary - ERP Integration Modernization

## 1. 背景

製造業Customer Cでは基幹ERPシステムと複数の社内システム（生産管理・在庫・購買）がポイントツーポイント連携しており、API管理の一元化と認証強化が求められていた。既存連携の技術負債が積み上がり、APIのオーナーシップや変更手順が整備されていなかった。ERPベンダーのサポート終了に向けた移行計画の一環として、APIレイヤーの近代化を提案する機会が生まれた。

## 2. 顧客課題

- 社内システム間のAPI連携が個別実装で乱立しており、セキュリティポリシーが不統一
- ERP APIのアクセス管理が不明確で、変更時の影響範囲が把握できない
- 非機能要件（レスポンスタイム・可用性）が文書化されておらず合意が難しい
- 移行期間中の責任分界が部門間で曖昧であり、実行体制が確立できていない
- ピーク負荷条件（バッチ処理との重複時間帯）が不明確

## 3. 主要要件

| 要件 | 優先度 |
|---|---|
| Microsoft Entra ID認証による保護 | High |
| ERPへの過剰リクエスト防止のレート制限 | High |
| 既存連携維持のためのAPIバージョン管理 | High |
| ERP操作の監査ログ記録 | High |
| API連携の可観測性基盤 | Medium |
| 製造ラインへの影響を最小化したゼロダウンタイム移行 | High |

## 4. 提案／実装内容

Azure API ManagementをERP APIのゲートウェイとして設置し、Entra ID認証・レート制限・バージョン管理を統合することを提案した。ただし提案段階でAPIオーナーの確定と非機能要件の合意が完了していないことから、Discoveryフェーズの先行実施を推奨した。

## 5. 主要リスクと対策

- **認証設定不備**: 認証設定のレビューと検証テストを計画
- **ピーク負荷**: バッチ処理との重複時間帯の事前調査が必要
- **APIオーナー不明確**: 提案段階で未解決のCriticalリスク

## 6. 結果

競合他社の提案が採択され、失注した。

## 7. 再利用可能な教訓

- APIオーナーシップが確立していない状態でのERP近代化提案は、実行可能性への懸念が評価基準で大きなマイナスになる
- ERPの移行案件では非機能要件（SLA・ピーク負荷・RPO/RTO）の事前合意なしに提案を進めると失注リスクが高い
- Discoveryフェーズを先行提案することで、実現可能性を顧客と共に確認しながら進める方式が有効

## 8. 再利用時の注意

- ERP連携案件では既存連携の完全なマッピングを提案前に依頼することが失注リスクを低減する
- 製造業のERP移行は業務停止リスクへの懸念が特に高いため、段階的実証を先行させる提案が有効
