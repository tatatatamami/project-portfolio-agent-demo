---
documentId: DOC-P004-RFP
projectId: P004
customerId: C002
title: P004 RFP Summary - Contact Center Knowledge Agent
documentType: RfpSummary
industry: Telecommunications
projectTheme: AI Agent Production
winLoss: Won
knowledgeStatus: Approved
confidentiality: Internal
sourceDate: 2024-04-01
tags:
  - ai-agent
  - contact-center
  - telecommunications
  - knowledge-management
  - acl
sourceUrl: https://demo.local/documents/P004/P004-rfp-summary
---

# P004 RFP Summary - Contact Center Knowledge Agent

## 1. 背景

通信事業者Customer Bのコンタクトセンターでは、オペレーター1人あたりの対応件数増加に伴いナレッジ検索時間が平均12分に達し、顧客待機時間が長期化していた。社内ナレッジは複数のシステムに分散しており、オペレーターが正確な情報を素早く見つけることが困難な状態だった。また、情報漏洩リスクとコンプライアンス要件から、オペレーターのロール別に参照可能な情報を厳密に制限する必要があった。AIエージェントによるナレッジ集約と権限管理の自動化が求められた。

## 2. 顧客課題

- オペレーターのナレッジ検索に平均12分かかり、顧客満足度が低下している
- 分散した社内ナレッジへのアクセスがロールによって異なり、手動管理に限界がある
- エージェントの回答精度が68%であり、業界標準の80%以上に届いていない
- エスカレーション率が35%と高く、上位オペレーターの負荷が増大している
- コンプライアンス要件から、回答内容の根拠記録が義務付けられている

## 3. 主要要件

| 要件 | 優先度 |
|---|---|
| オペレーターロール別ACLトリミング | High |
| 回答への根拠ドキュメント引用の必須化 | High |
| 定期的な評価パイプラインによる精度測定 | High |
| Content Safetyによる不適切情報の除外 | High |
| 高リスク問い合わせの上位エスカレーション | High |
| フィードバックとKPIの継続収集 | Medium |

## 4. 提案／実装内容

コンタクトセンター向けのACL対応ナレッジエージェントをFoundry Agentと Azure AI Searchの組み合わせで構築することを提案した。

## 5. 主要リスクと対策

- **ハルシネーション**: 引用必須化と評価パイプラインで継続検証
- **データ過剰共有**: オペレーターロール別ACLトリミングの二重実装
- **受け入れ基準未定義**: 本番前に精度・エスカレーション率を数値で合意

## 6. 結果

提案は採択され、プロジェクトP004として受注した。

## 7. 再利用可能な教訓

- コンタクトセンターのオペレーターロールはシフトや担当業務で複雑に変化するため、ACL設計に動的な権限反映が必要
- 回答根拠の記録義務は通信以外の規制業界（金融・医療など）でも標準要件になりやすい

## 8. 再利用時の注意

- ナレッジ移行前にコンテンツの棚卸しと権限マッピングを完了させること
- 非規制業界ではContent Safetyの設定レベルを業務内容に合わせて調整すること
