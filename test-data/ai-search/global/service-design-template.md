---
documentId: DOC-GLOBAL-TEMPLATE
projectId: GLOBAL
customerId: GLOBAL
title: Service Design Template
documentType: Template
industry: Cross-industry
projectTheme: Cross-theme
winLoss: N/A
knowledgeStatus: Approved
confidentiality: Internal
sourceDate: 2024-01-01
tags:
  - template
  - service-design
  - standard-service
  - offering
  - assetization
sourceUrl: https://demo.local/documents/global/service-design-template
---

# Service Design Template

## 目的

本テンプレートは、複数案件の横断分析から抽出した共通パターンを、標準サービスまたはオファリング候補として整理するための構造を提供する。

---

## 標準サービス候補の出力形式

サービス資産化エージェントが標準サービス候補を生成する際は、以下のセクションを含める。

### A. サービス候補名

- 簡潔で再利用可能な表現を使用する
- 業種・顧客に依存しない汎用名称とする
- 例: `AI-ready Data Foundation Service`、`Secure API Modernization Service`

### B. 対象顧客・業種

- 最も適合する業種・顧客セグメントを記述する
- 複数業種への適用可能性も示す
- 例: 製造業・小売業・物流業（大量センサー/トランザクションデータを持つエンタープライズ）

### C. 共通する顧客課題

- 複数案件に共通して確認された課題を列挙する
- 「確立した共通パターン」（3件以上）のみを含める
- 課題は一般化された表現を使用し、特定顧客を識別できる記述を避ける

### D. 標準要件

- 4案件以上に共通して要求された機能要件を列挙する
- 優先度（必須/推奨/オプション）を付与する
- 例:
  - **必須**: Unified Data Model、Data Quality Rules、Semantic Model
  - **推奨**: Data Lineage、Near-real-time Ingestion
  - **オプション**: AI Metadata Tagging、Data Catalog

### E. 標準機能・アーキテクチャ

- 共通して実装された機能コンポーネントを列挙する
- 推奨アーキテクチャの概要を示す
- 技術スタックの選択肢を示す（ベンダー依存の表現を避ける）

### F. 標準提供プロセス

- Discovery → 設計 → 構築 → 移行 → 本番化の各フェーズを定義する
- 各フェーズの概算期間と主要成果物を示す
- 例:
  - **Phase 1 Discovery** (2週間): データオーナー確定・非機能要件合意・リスク評価
  - **Phase 2 設計** (4週間): Unified Data Model・パイプライン設計・Semantic Model定義
  - **Phase 3 構築** (8週間): Lakehouse構築・パイプライン実装・Data Agent設定
  - **Phase 4 移行** (4週間): 段階移行・品質検証・本番稼働準備
  - **Phase 5 本番化** (2週間): 本番稼働・監視体制確立・ナレッジ移転

### G. 共通リスクと対策

- 複数案件に共通して確認されたリスクを列挙する
- 各リスクの実績Mitigationを記述する
- 例:
  - **データオーナー不明確 (Medium)**: Discovery Phaseを先行実施して確定する
  - **ソース間不整合 (High)**: パイプライン内の整合性チェックと自動アラート

### H. 期待する事業価値

- 複数案件の実績から抽出した定量的な改善指標を示す
- Actual/Projectedの区別を明記する
- 例:
  - 分析準備時間: 平均 -75%（P005・P007・P009・P012の実績）
  - 計画サイクル短縮: 平均 -62%（P005・P007・P012の実績）

### I. 根拠となるProjectID・数値・文書タイトル

- 主張の根拠となるProjectIDと数値を必ず記載する
- 文書タイトルとDocumentIDを参照として含める
- 例:
  - 対象案件: P005、P007、P009、P012（AI-ready Data Foundation）
  - 平均利益率: 32.0%（project-financials.csvの実績値）
  - 参考文書: `P005 Retrospective`（DOC-P005-RETRO）

### J. 追加検証が必要な点

- 根拠が不十分な主張を明示する
- 追加データ収集が必要な仮説を記述する
- 例:
  - 現時点では4案件のデータのみ。8案件以上に拡張して統計的信頼性を高める必要がある
  - 海外展開案件でのパターン適用可能性は未検証

---

## 分析品質チェックリスト

サービス候補を生成する際は以下を確認すること。

- [ ] 共通パターンの根拠は3件以上か
- [ ] 単一案件の特性を共通パターンと呼んでいないか
- [ ] Actual OutcomeとProjected Outcomeを混在させていないか
- [ ] Draftデータを根拠に使用していないか
- [ ] 特定顧客を識別できる表現を使っていないか
- [ ] 数値の単位と出典が明記されているか
