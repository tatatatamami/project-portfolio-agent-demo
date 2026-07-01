---
documentId: DOC-P006-BIDR
projectId: P006
customerId: C003
title: P006 Bid Review - ERP Integration Modernization
documentType: BidReview
industry: Manufacturing
projectTheme: API Modernization
winLoss: Lost
knowledgeStatus: Approved
confidentiality: Internal
sourceDate: 2024-05-31
tags:
  - bid-review
  - api-modernization
  - erp-integration
  - lost-deal
  - lessons-learned
sourceUrl: https://demo.local/documents/P006/P006-bid-review
---

# P006 Bid Review - ERP Integration Modernization

## 1. 背景

ERP統合API近代化の商談は2024年3月から5月にかけて進行し、最終的に競合他社が採択された。本Bid Reviewは失注要因と次回の改善策を記録する。

## 2. 顧客課題

Customer CのERP APIには明確なオーナーシップが存在せず、移行期間中の責任体制も不明確であった。これが提案の実行可能性評価において最大の障害となった。

## 3. 主要要件

技術要件6件の提案自体に問題はなかったが、前提条件の整備なしに要件を提案したことが評価を下げた。

## 4. 提案／実装内容

Azure API Management・Entra ID認証・レート制限・バージョン管理・可観測性を含む技術提案を行ったが、実行可能性の前提条件を顧客と共に確認する機会が不足していた。

## 5. 主要リスクと対策

提案書でAPIオーナー不明確（Critical）を明示したが、リスクの記載だけでは顧客の懸念を払拭できなかった。

## 6. 結果

**失注要因の分析**:

1. **既存ERP連携のAPIオーナーが不明確**: 複数部門間でAPIの変更権限と移行責任が合意されておらず、誰が意思決定者か不明確なまま提案を進めた。競合他社は提案前にステークホルダーマッピングを実施し、この問題を事前に解消して提案に臨んでいた。

2. **移行期間中の責任分界が合意されなかった**: 移行期間中に問題が発生した場合の責任範囲が不明確なまま提案書を提出した。製造業ではライン停止の責任問題が極めてセンシティブであり、責任分界の明確化なしに提案を進めたことが最大の失注要因となった。

3. **非機能要件とピーク負荷条件が未確定**: バッチ処理とAPIアクセスが重複する時間帯の負荷条件が合意されておらず、提案したレート制限値の根拠が弱かった。競合他社はDiscovery実施後に具体的な数値を提示していた。

4. **価格以前に実行可能性への懸念が残った**: 評価委員会では技術の優劣より「本当に実行できるか」の議論が中心であったことが後のヒアリングで判明した。実行可能性の懸念が払拭できなかったため価格評価まで進まなかった。

5. **次回はDiscoveryフェーズを先行提案する**: 提案前に2週間のDiscoveryフェーズを設けてAPIオーナーの確定・非機能要件の合意・責任分界の確認を完了させてから技術提案を行う体制に変更する。

## 7. 再利用可能な教訓

- ERP連携近代化は「技術的に正しい提案」よりも「実行可能性の証明」が評価の鍵である
- Discoveryフェーズの先行提案は、顧客のリスク感度が高い案件では受注率を高める
- 製造業の提案では責任分界の明確化を提案書の主要要素として組み込む

## 8. 再利用時の注意

- APIオーナーが不在の案件では、提案前のDiscoveryが事実上の前提条件である
- 製造業以外でも、基幹システムの近代化案件では同様のアプローチが有効
