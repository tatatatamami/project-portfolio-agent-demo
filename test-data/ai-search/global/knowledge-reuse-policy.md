---
documentId: DOC-GLOBAL-POLICY
projectId: GLOBAL
customerId: GLOBAL
title: Knowledge Reuse Policy
documentType: Policy
industry: Cross-industry
projectTheme: Cross-theme
winLoss: N/A
knowledgeStatus: Approved
confidentiality: Internal
sourceDate: 2024-01-01
tags:
  - policy
  - knowledge-reuse
  - governance
  - data-classification
  - approval
sourceUrl: https://demo.local/documents/global/knowledge-reuse-policy
---

# Knowledge Reuse Policy

## 1. 目的

本ポリシーは、案件を通じて蓄積された知識・教訓・提案パターンを、匿名化・承認済みの状態で組織全体の共有資産として活用するためのルールを定める。

## 2. データの前提

本リポジトリに格納されているすべてのデータおよびドキュメントは、以下の前提のもとで管理されている。

- **匿名化済み**: 実顧客名・実案件名・実担当者名はすべて仮名（Customer A、P001等）に置き換えられている
- **承認済み**: KnowledgeStatus=Approvedのデータは、情報オーナーの承認を経て共有資産として登録されたものである
- **Draft除外**: KnowledgeStatus=Draftのデータは承認プロセス中であり、分析・引用の対象外とする

## 3. 使用可能なデータの分類

| KnowledgeStatus | 説明 | 使用可否 |
|---|---|---|
| Approved | 匿名化・承認済み。共有資産として利用可能 | ✅ 使用可 |
| Draft | 審査中。承認前の状態 | ❌ 使用不可 |

## 4. AIエージェントの使用ルール

AIエージェント（サービス資産化エージェント）は以下のルールに従って動作する。

1. KnowledgeStatus=Approvedのデータと文書のみを分析・引用の対象とする
2. 実在企業・実案件・実在人物を推測・言及しない
3. 特定の顧客を識別できる情報を回答に含めない
4. Lost案件のProjected Outcomeを実績値として扱わない
5. データの更新・承認・公開・書き戻しを行わない

## 5. 共通パターンの認定基準

| パターン分類 | 基準 | 表現 |
|---|---|---|
| 確立した共通パターン | 3件以上の異なる案件に共通 | 「確立した共通パターン」 |
| 初期的なパターン | 2件のみに共通 | 「初期的なパターン」 |
| 単一案件の特性 | 1件のみ | 共通パターンと呼ばない |

## 6. 引用の義務

AIエージェントが共通パターンや根拠を提示する場合は、必ず以下を明記すること。

- 根拠となるProjectID（例：P005、P007、P009、P012）
- 参照した数値と出典CSV
- 参照した文書タイトルとDocumentID

## 7. 再利用の禁止事項

- 承認前のデータを分析に使用すること
- 特定の顧客・案件を識別できる形での共有
- データの無断改変
- 実顧客への直接的な言及
