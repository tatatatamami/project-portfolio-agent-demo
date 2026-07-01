---
documentId: DOC-P001-RETRO
projectId: P001
customerId: C001
title: P001 Retrospective - Game LiveOps API Modernization
documentType: Retrospective
industry: Gaming
projectTheme: API Modernization
winLoss: Won
knowledgeStatus: Approved
confidentiality: Internal
sourceDate: 2024-06-30
tags:
  - retrospective
  - api-modernization
  - partner-onboarding
  - gaming
  - lessons-learned
sourceUrl: https://demo.local/documents/P001/P001-retrospective
---

# P001 Retrospective - Game LiveOps API Modernization

## 1. 背景

Game LiveOps API近代化プロジェクトは2024年1月から6月にかけて実施した。パートナー向けAPIをAzure API Managementを中心としたゲートウェイアーキテクチャへ移行し、認証統一・レート制限・バージョン管理・可観測性の4機能を新たに導入した。

## 2. 顧客課題

移行前、パートナーオンボーディングに平均20日を要し、月次インシデントが12件発生していた。デプロイは月2回しかできず、LiveOpsのビジネス要件に対応できていなかった。

## 3. 主要要件

6つの要件（認証・レート制限・バージョン管理・監査ログ・可観測性・ゼロダウンタイム移行）をすべて計画通りに実装完了した。

## 4. 提案／実装内容

Azure API Managementの導入、Entra ID認証統合、クライアント別レート制限、バージョン管理機構、OpenTelemetry分散トレーシングの5機能を順次リリースした。

## 5. 主要リスクと対策

認証設定不備は事前ペネトレーションテストで対処し、ピーク負荷は負荷試験と自動スケーリング設定で解消した。すべてのリスクをMitigatedとして移行を完了した。

## 6. 結果

| 指標 | 移行前 | 移行後 | 改善 |
|---|---:|---:|---:|
| パートナーオンボーディング日数 | 20日 | 6日 | -70% |
| 月次インシデント件数 | 12件 | 8件 | -33% |
| 月次デプロイ回数 | 2回 | 8回 | +300% |

収益: 480百万円、利益: 135百万円（利益率28.1%）、工数削減率: 30%

## 7. 再利用可能な教訓

- **ポリシーのコード管理**: API Managementのポリシー定義をGitで管理することで、チームレビューとロールバックが格段に容易になった
- **段階認証移行**: パートナーグループ単位での認証移行は、全体移行より障害範囲が限定されリスクが低い
- **可観測性ファースト**: トレーシングの後付けは困難なため、開発初期から組み込む設計が重要
- **廃止スケジュール通知**: バージョン廃止は6ヶ月前の事前通知でパートナーとのトラブルをほぼゼロにできた

## 8. 再利用時の注意

- API ManagementのSKUはトラフィック規模に合わせて選定すること（開発層は本番負荷に不適）
- LiveOps業界特有のイベントスパイクを考慮したレート制限設計が必要であり、他業界ではトラフィックパターンが異なる
- 既存パートナー数が多い場合、ゼロダウンタイム移行の期間は6ヶ月以上を見込むこと
