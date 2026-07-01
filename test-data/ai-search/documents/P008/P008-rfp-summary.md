---
documentId: DOC-P008-RFP
projectId: P008
customerId: C004
title: P008 RFP Summary - Store Operations AI Assistant
documentType: RfpSummary
industry: Retail
projectTheme: AI Agent Production
winLoss: Won
knowledgeStatus: Approved
confidentiality: Internal
sourceDate: 2024-05-01
tags:
  - ai-agent
  - retail
  - store-operations
  - compliance
  - access-control
sourceUrl: https://demo.local/documents/P008/P008-rfp-summary
---

# P008 RFP Summary - Store Operations AI Assistant

## 1. 背景

小売事業者Customer Dでは全国の店舗スタッフが業務手順・商品情報・コンプライアンス規則を参照するために毎回本部問い合わせを行っており、店舗スタッフ1人あたりの業務完了時間が40分に達していた。情報検索だけで15分かかる状況が常態化し、規制遵守の確認漏れも頻発していた。店舗スタッフの職種・担当エリアによって参照可能な情報が異なるため、権限管理と情報提供の自動化が求められた。

## 2. 顧客課題

- 店舗スタッフの業務完了に平均40分かかり生産性が低い
- 情報検索に15分を要し、本来の業務に集中できない
- コンプライアンス確認の漏れが月次で発生し、規制対応コストが高い
- 職種によって参照すべき情報が異なるが、手動のACL管理が困難
- 商品・価格・在庫情報が頻繁に更新されナレッジが陳腐化しやすい

## 3. 主要要件

| 要件 | 優先度 |
|---|---|
| 職種別ACLトリミング | High |
| 業務マニュアルへの根拠引用 | High |
| 店舗業務品質の評価パイプライン | High |
| コンプライアンス情報のContent Safety | High |
| 緊急対応問い合わせのエスカレーション | High |
| スタッフフィードバック収集 | Medium |

## 4. 提案／実装内容

店舗スタッフのロール別ACL対応ナレッジエージェントをFoundry AgentとAzure AI Searchで構築することを提案した。

## 5. 主要リスクと対策

- **ハルシネーション**: 業務手順への根拠引用を必須化
- **データ過剰共有**: 職種別ACLトリミングを実装
- **ナレッジ陳腐化**: 商品・価格更新トリガーによるナレッジ自動更新を設計

## 6. 結果

提案は採択され、プロジェクトP008として受注した。

## 7. 再利用可能な教訓

- 多店舗展開の小売業では職種・地域・シフトに応じた複雑なACL設計が必要であり、設計フェーズに十分な工数を確保する
- コンプライアンス関連情報のContent Safety設定は業種の規制内容に合わせて専門家とレビューする

## 8. 再利用時の注意

- 小売業の商品情報は更新頻度が高いため、ナレッジ更新の自動化が品質維持の必須要件となる
- 多店舗展開では店舗タイプ（旗艦店・標準店・小型店）によってロール定義が異なる場合がある
