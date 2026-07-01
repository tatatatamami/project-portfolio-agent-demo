---
documentId: DOC-P010-PROP
projectId: P010
customerId: C005
title: P010 Proposal Summary - Creator Support Agent
documentType: ProposalSummary
industry: Media
projectTheme: AI Agent Production
winLoss: Lost
knowledgeStatus: Approved
confidentiality: Internal
sourceDate: 2024-07-01
tags:
  - ai-agent
  - media
  - creator-support
  - proposal
  - lost
sourceUrl: https://demo.local/documents/P010/P010-proposal-summary
---

# P010 Proposal Summary - Creator Support Agent

## 1. 背景

メディアコンテンツクリエイターのサポート問い合わせ急増に対応するため、クリエイター別ACL対応AIエージェントの構築を提案した。データ権限整理が未完了のまま提案を進めたことが後の失注につながった。

## 2. 顧客課題

問い合わせ急増・権限管理困難・回答精度58%・データ権限未整理・本番責任未確定という5課題への対応を提案した。

## 3. 主要要件

6要件への技術的対応を提案した。

## 4. 提案／実装内容

Foundry AgentとAzure AI Searchを組み合わせたクリエイター向けACL対応ナレッジエージェントを提案した。クリエイターのロール（一般クリエイター・パートナー・プレミアムパートナー）と契約種別に基づくACLトリミング、著作権・ライセンスの根拠引用必須化、評価パイプライン、専門家エスカレーションの4機能を中核として設計した。

ただし、以下の前提条件が未確定であることを提案書に明記した:
- クリエイターごとのデータアクセス権限マッピングが未整理
- 収益データ・権利情報の情報オーナーが確定していない
- 本番稼働後の評価指標・精度基準・エスカレーション条件が未合意
- 本番運用の責任者（社内担当部門）が未決定

これらの解消のため、AI Production Readiness Assessment（4週間・概算300万円）の先行実施を推奨した。

## 5. 主要リスクと対策

データ過剰共有（High）と受け入れ基準未定義（Critical）の2つのOpenリスクを提案書に明示した。これらの解消なしには本番稼働の準備が整わないことを説明した。

## 6. 結果

競合他社の提案が採択され、失注した。提案後のヒアリングでは以下が判明した:
- 競合他社はPoCデモを積極的に提示し、実現可能性の印象を強く与えた
- 我々の提案は前提条件の不備を正直に記載したが、それが「準備不足」と受け取られた
- 本番移行計画の具体性では競合他社が優れていた

## 7. 再利用可能な教訓

- データ権限整理が完了していない状況での提案は、正直な記載が「準備不足」と評価されるジレンマがある
- AI Production Readiness Assessmentの先行提案は、顧客の準備状況によって前向きに評価される場合とそうでない場合がある
- PoCデモの提示は技術実現可能性への懸念を払拭する強力な手段であり、権限問題が残る中でもデモで信頼を得る競合への対策が必要

## 8. 再利用時の注意

- クリエイター向けサービスでは収益データへのアクセスが法的リスクと直結するため、権限整理の完了を絶対条件とすること
- 本番移行計画の具体性（タイムライン・コスト・SLA）を提案書の主要要素として強化すること
