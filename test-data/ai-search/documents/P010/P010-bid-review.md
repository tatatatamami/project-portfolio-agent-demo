---
documentId: DOC-P010-BIDR
projectId: P010
customerId: C005
title: P010 Bid Review - Creator Support Agent
documentType: BidReview
industry: Media
projectTheme: AI Agent Production
winLoss: Lost
knowledgeStatus: Approved
confidentiality: Internal
sourceDate: 2024-09-30
tags:
  - bid-review
  - ai-agent
  - media
  - lost-deal
  - production-readiness
sourceUrl: https://demo.local/documents/P010/P010-bid-review
---

# P010 Bid Review - Creator Support Agent

## 1. 背景

クリエイターサポートAIエージェントの商談は2024年7月から9月にかけて進行し、競合他社が採択された。本Bid Reviewは失注要因と次回の改善策を記録する。

## 2. 顧客課題

クリエイターサポートの問い合わせ急増・権限管理困難・回答精度不足・データ権限未整理・本番責任未確定という5課題が確認されていた。

## 3. 主要要件

技術要件6件の提案内容に根本的な問題はなかったが、前提条件の整備状況が本番化への評価を下げた。

## 4. 提案／実装内容

ACL-aware Retrieval・Citation and Grounding・Evaluation Pipeline・Content Safety・Human Escalationを提案した。

## 5. 主要リスクと対策

データ過剰共有（High/Open）と受け入れ基準未定義（Critical/Open）を提案書に明示したが、解消策の提示が不十分だった。

## 6. 結果

**失注要因の分析**:

1. **データ利用権限と情報オーナーが未整理**: クリエイターの収益データ・権利情報へのアクセス権限がシステム的に整理されていなかった。提案書で正直にリスクを記載したが、競合他社はPoCデモで「動くもの」を見せることで顧客の不安を払拭した。本質的な権限問題は未解決のまま競合提案が採択されたが、この判断の正しさは本番稼働後に明らかになる。

2. **評価指標、精度基準、エスカレーション条件が未定義**: 提案段階で精度目標・エスカレーション条件・KPIが顧客と合意されていなかった。「何を持って成功とするか」を顧客側が明確にできていないにもかかわらず、競合他社は「成功事例」の見せ方が上手く評価を得た。

3. **本番運用責任者が不明確**: 本番稼働後の運用責任部門が社内で決まっておらず、提案段階でこの問題を指摘したことが「問題ばかりを指摘する提案」と受け取られた可能性がある。

4. **PoCデモは評価されたが本番移行計画が弱かった**: 評価セッションで実施したPoCデモは好評だったが、本番環境への移行タイムライン・SLA・コストの具体性で競合他社に劣った。

5. **次回はAI Production Readiness Assessmentを先行提案する**: 本番稼働の前提条件を顧客と共に整備するAI Production Readiness Assessment（権限整理・受け入れ基準合意・運用責任確定）を先行フェーズとして提案し、前提条件を解消してから本番化提案を行う体制に変更する。

## 7. 再利用可能な教訓

- **権限問題の正直な記載の代償**: リスクを正直に記載することが「準備不足」と評価されるジレンマは、PoCデモとReadiness Assessmentの先行提案で解消できる
- **本番移行計画の具体性**: タイムライン・SLA・移行コストを定量的に示すことが競合への対抗策として有効
- **受け入れ基準の先行合意**: 提案初期段階での精度目標・KPI・エスカレーション条件の合意が採択率に直結する

## 8. 再利用時の注意

- クリエイター・コンテンツ権利・収益情報が絡み合う案件では、AI Production Readiness Assessmentの先行提案を標準プロセスとすること
- PoCデモは技術実現可能性を示す最も効果的な手段であり、権限問題が残る状況でも実現可能な範囲でデモを準備すること
