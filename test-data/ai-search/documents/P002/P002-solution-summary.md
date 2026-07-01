---
documentId: DOC-P002-SOL
projectId: P002
customerId: C001
title: P002 Solution Summary - Player Support AI Agent
documentType: SolutionSummary
industry: Gaming
projectTheme: AI Agent Production
winLoss: Won
knowledgeStatus: Approved
confidentiality: Internal
sourceDate: 2024-05-01
tags:
  - grounded-retrieval
  - acl-aware-retrieval
  - evaluation-pipeline
  - human-escalation
  - gaming
sourceUrl: https://demo.local/documents/P002/P002-solution-summary
---

# P002 Solution Summary - Player Support AI Agent

## 1. 背景

ゲームプレイヤーサポートの問い合わせ急増に対応するため、ACL対応のナレッジ検索を中核とした本番グレードAIエージェントを構築した。

## 2. 顧客課題

問い合わせ急増・権限管理・根拠なし回答のリスク・品質劣化検知の困難さという4つの課題を解決する必要があった。

## 3. 主要要件

6要件すべてを実装完了した。

## 4. 提案／実装内容

**Grounded Retrieval**: Azure AI Searchのゲームコンテンツインデックスからプレイヤーのロール（一般・プレミアム・βテスター等）に応じた文書のみを検索し、回答根拠として使用した。検索ヒット率と関連性スコアを閾値として回答生成の可否を制御した。

**ACL-aware Retrieval**: ユーザーのIDトークンに含まれるロールとゲームタイトルのACL設定を照合し、権限外コンテンツを検索クエリ段階で除外した。プレイヤーデータへのアクセスは厳密なスコープ制限のもとに実装した。

**Source Display**: 回答本文にゲームガイドのページ名と引用箇所を表示し、プレイヤーが内容の根拠を確認できるようにした。引用が表示できない場合はエスカレーションパスに自動転送する設計とした。

**Evaluation Pipeline**: 週次で回答サンプルを自動評価し、精度・根拠有効性・安全性・エスカレーション率の4指標をダッシュボードで可視化した。指標低下を検知した場合はナレッジ更新とプロンプト調整のサイクルを実行した。

**Human Escalation and Monitoring**: エスカレーション条件（根拠なし・高リスクキーワード・否定的感情スコア）を設定し、条件一致時に人間のサポートエージェントへ自動転送するルーティングを実装した。

## 5. 主要リスクと対策

ハルシネーション・データ過剰共有・古いナレッジ・受け入れ基準未定義の4リスクをすべてMitigatedとした。

## 6. 結果

平均対応時間14分→9分、初回応答10分→4分、セルフサービス解決率0%→22%を達成した。

## 7. 再利用可能な教訓

- ACLトリミングは検索クエリ生成前に適用することで根本的なデータ過剰共有リスクを排除できる
- 評価パイプラインの指標は本番開始時点で顧客と合意しておくことが後のトラブルを防ぐ
- Content Safetyの設定はゲームジャンルに応じてカスタマイズが必要（アクションゲームとキッズゲームで許容範囲が異なる）
- エスカレーション条件の初期設定は保守的（転送多め）に設定し、データを見て徐々に緩和する方が安全

## 8. 再利用時の注意

- ゲーム特有のコンテンツ構造（タイトル・バージョン・言語）に合わせてインデックス設計を再検討すること
- 非ゲーム業界では「ロール」の定義と権限モデルが全く異なるため、ACL設計を一から検討すること
- 評価指標のベースライン値は業種とユースケースによって大きく異なる
