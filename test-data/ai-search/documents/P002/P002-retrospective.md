---
documentId: DOC-P002-RETRO
projectId: P002
customerId: C001
title: P002 Retrospective - Player Support AI Agent
documentType: Retrospective
industry: Gaming
projectTheme: AI Agent Production
winLoss: Won
knowledgeStatus: Approved
confidentiality: Internal
sourceDate: 2024-10-31
tags:
  - retrospective
  - ai-agent
  - self-service
  - gaming
  - lessons-learned
sourceUrl: https://demo.local/documents/P002/P002-retrospective
---

# P002 Retrospective - Player Support AI Agent

## 1. 背景

プレイヤーサポートAIエージェントは2024年4月から10月にかけて開発・本番稼働を完了した。ACL対応Grounded Retrieval・評価パイプライン・人間エスカレーションの3機能が本番品質の中核となった。

## 2. 顧客課題

問い合わせ急増・権限管理・回答品質・品質監視という4課題を本プロジェクトで解決した。

## 3. 主要要件

6要件すべてを実装し、本番稼働後も継続して品質指標を充足している。

## 4. 提案／実装内容

Grounded Retrieval・ACL-aware Retrieval・Source Display・Evaluation Pipeline・Human Escalationの5機能を実装した。

## 5. 主要リスクと対策

4つの特定リスクをすべてMitigatedとし、本番稼働後の品質劣化も発生していない。

## 6. 結果

| 指標 | 導入前 | 導入後 | 改善 |
|---|---:|---:|---:|
| 平均対応時間 | 14分 | 9分 | -35.7% |
| 初回応答時間 | 10分 | 4分 | -60.0% |
| セルフサービス解決率 | 0% | 22% | +22pt |

収益: 320百万円、利益: 78百万円（利益率24.4%）、工数削減率: 25%

## 7. 再利用可能な教訓

- **週次評価の習慣化**: 評価パイプラインを週次自動実行にすることで品質劣化を2週間以内に検知できた
- **エスカレーション率の逆説**: エスカレーション率が下がりすぎると、本来転送すべき問い合わせを取りこぼしているサインである可能性がある
- **ナレッジ更新の優先度**: ゲームアップデート直後の72時間は特にナレッジの陳腐化が速く、即時更新プロセスが必須
- **プレイヤー感情の可視化**: 否定的感情スコアの監視がエスカレーション精度を大幅に向上させた

## 8. 再利用時の注意

- ゲームのコンテンツ更新頻度は他業種より格段に高く、ナレッジ更新サイクルの設計はゲーム特有の要件に基づいている
- 他業界では「本番稼働後のナレッジ更新責任者」を事前に明確化しておくことが重要
- セルフサービス率の目標値はビジネスモデルと問い合わせ複雑度によって大きく異なる
