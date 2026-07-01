---
documentId: DOC-P006-PROP
projectId: P006
customerId: C003
title: P006 Proposal Summary - ERP Integration Modernization
documentType: ProposalSummary
industry: Manufacturing
projectTheme: API Modernization
winLoss: Lost
knowledgeStatus: Approved
confidentiality: Internal
sourceDate: 2024-03-01
tags:
  - api-modernization
  - erp-integration
  - manufacturing
  - proposal
  - lost
sourceUrl: https://demo.local/documents/P006/P006-proposal-summary
---

# P006 Proposal Summary - ERP Integration Modernization

## 1. 背景

製造業Customer CのERPシステムAPIを段階的に近代化し、認証統一と可観測性強化を実現する技術提案を行った。提案段階でAPIオーナーシップの整理が完了していない課題が残っていた。

## 2. 顧客課題

ERP APIのセキュリティ不統一・オーナーシップの不明確さ・非機能要件の未定義が主要課題として確認されていた。

## 3. 主要要件

認証統一・レート制限・APIバージョン管理・監査ログ・可観測性・ゼロダウンタイム移行の6要件を提案した。

## 4. 提案／実装内容

Azure API ManagementをERP APIのゲートウェイとして設置し、Microsoft Entra ID認証・クライアント別レート制限・URLパスバージョニング・監査ログの4機能を実装するアーキテクチャを提案した。既存の社内システム連携を維持しながら段階的にAPIレイヤーを切り替えるゼロダウンタイム移行計画を含めた。可観測性基盤としてOpenTelemetryによる分散トレーシングの導入も提案した。

ただし、以下の条件を提案段階での懸念事項として明示した:
- 既存ERPインターフェースのAPIオーナーが部門間で確定していないこと
- 非機能要件（レスポンスタイム・可用性SLA・ピーク負荷条件）が合意されていないこと
- 移行期間中の責任分界が未決定であること

これらの解消のため、提案実施前にDiscoveryフェーズ（2週間・概算150万円）の先行実施を推奨した。

## 5. 主要リスクと対策

APIオーナー不明確（Critical）を筆頭に、ピーク負荷・Breaking Changeのリスクを明示した。APIオーナーの確定なしには移行開始の判断ができないことを提案書に記載した。

## 6. 結果

競合他社の提案が採択され、失注した。評価後のヒアリングでは、価格以前に実行可能性への懸念が評価委員会の議論で大きな比重を占めていたことが判明した。

## 7. 再利用可能な教訓

- 提案段階でAPIオーナーが不明確な場合は、Discoveryフェーズを先行提案として分離することで、実行可能性への懸念を解消できる
- 非機能要件の未合意は、技術提案の価値を顧客が判断できなくなる根本的な問題であり、提案前の合意が重要
- 製造業のERPは業務停止リスクへの感度が特に高く、「実行できるか」の確信を顧客に与えることが技術力と同等に重要

## 8. 再利用時の注意

- ERP連携案件では既存API連携の全体マッピング（連携先システム・データ量・更新頻度）を提案前に入手することを前提条件とすること
- Discoveryフェーズの先行提案は、顧客によっては「準備不足」と受け取られるリスクがあるため、提案の文脈を丁寧に説明すること
