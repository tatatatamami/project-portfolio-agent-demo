# Portfolio Analysis Workload

`test-data` 配下の複数案件データを読み込み、Service Portfolio Executive Cockpit が表示できる派生データ JSON を生成するローカル分析バッチです。DB、Web 画面、チャット画面は変更しません。

## 責任分担

Python コードは、案件数、受注率、売上、利益、平均利益率、平均工数削減率、根拠案件数、業種数、共通要件数、共通機能数を確定計算します。LLM は、経営層向け要約、事業化理由、再利用資産、標準化ギャップ、推奨事業モデル、リスク、90 日アクションなどの文章生成だけを担当します。

数値は LLM に再計算させません。LLM が返した案件 ID、文書 ID、sourceId、数値は検証し、不一致がある場合は `dashboard-data.json` を出力しません。

## 入力データ

- `test-data/fabric/customers.csv`: 顧客マスタ。`CustomerID` を案件マスタと関連付けます。
- `test-data/fabric/projects.csv`: 案件マスタ。`ProjectID`、`CustomerID`、`ProjectTheme`、`WinLoss` が分析の主要キーです。
- `test-data/fabric/opportunities.csv`: 商談情報。`ProjectID` で案件に紐づきます。
- `test-data/fabric/proposals.csv`: 提案情報。`ProposalID` は sourceId として検証対象です。
- `test-data/fabric/project-financials.csv`: 売上、原価、利益、利益率、工数削減率。数値集計の正本です。
- `test-data/fabric/requirements.csv`: 要件。`RequirementName` をテーマごとの共通要件検出に使います。
- `test-data/fabric/features.csv`: 機能。`FeatureName` をテーマごとの再利用資産候補検出に使います。
- `test-data/fabric/risks.csv`: リスク。`RiskName` を候補ごとの主要リスク生成に使います。
- `test-data/fabric/business-outcomes.csv`: 成果指標。`OutcomeID` は sourceId として検証対象です。
- `test-data/ai-search/documents/**/*.md`: 案件文書。YAML Front Matter の `documentId`、`projectId`、`winLoss`、`industry`、`projectTheme` を検証します。
- `test-data/ai-search/global/*.md`: グローバル文書。`projectId: GLOBAL` として扱います。
- `test-data/expected/*.json`: 期待値と検証ルール。正解値がある項目は LLM 出力よりこちらを優先します。

## 出力データ

- `analysis/output/dashboard-data.json`: Executive Cockpit 表示用データ。検証成功時のみ出力します。
- `analysis/output/analysis-run.json`: 実行メタデータ、読み込み件数、候補数、LLM 呼び出し回数、検証概要。
- `analysis/output/validation-report.json`: 入力・出力検証結果。
- `analysis/output/llm-input.json`: `--save-debug-files` 指定時のみ。LLM 入力確認用。
- `analysis/output/llm-raw-output.json`: `--save-debug-files` 指定時のみ。LLM 生出力確認用。

## スコア基準

各スコアは 0 から 100 の整数です。LLM の自由判断ではなく、Python が計算した実績値と明示基準から算出します。

- `profitability`: 平均利益率と受注売上を重視します。
- `reusability`: 共通機能数、対象業種数、根拠案件数を重視します。
- `standardization`: 共通要件数と共通機能数を重視します。
- `recurringRevenue`: 工数削減率と運用・監視に転用しやすい共通機能数を重視します。
- `saasReadiness`: 共通要件数、共通機能数、失注件数による標準化難度を組み合わせます。
- `feasibility`: 失注件数と平均工数削減率から実行しやすさを見ます。
- `confidence`: 根拠案件数、根拠文書数、業種数を重視します。
- `priority`: 上記を重み付けした総合優先度です。

## セットアップ

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r analysis/requirements.txt
az login
```

`.env.example` を参考に `.env` を作成してください。`.env` と API Key は Git 管理外です。

## Azure OpenAI 設定

DefaultAzureCredential を使う場合:

```text
AZURE_AUTH_MODE=default-credential
AZURE_OPENAI_ENDPOINT=https://<account>.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=<deployment-name>
AZURE_OPENAI_API_VERSION=2024-10-21
ANALYSIS_MODEL_PROVIDER=azure-openai
```

API Key を使う場合:

```text
AZURE_AUTH_MODE=api-key
AZURE_OPENAI_ENDPOINT=https://<account>.openai.azure.com/
AZURE_OPENAI_API_KEY=<secret>
AZURE_OPENAI_DEPLOYMENT=<deployment-name>
```

## Foundry 設定

`.env.example` には Foundry 用の変数も用意しています。現時点の実装は Azure OpenAI のローカル呼び出しを実装済みで、`--provider foundry` は将来拡張用です。

## 実行方法

Azure 接続なしで、入力読み込み、確定集計、検証、出力生成だけを実行します。

```powershell
python analysis/analyze_portfolio.py --dry-run --verbose
```

Azure OpenAI を使って文章生成まで行います。

```powershell
python analysis/analyze_portfolio.py --provider azure-openai --verbose
```

主なオプション:

- `--input-dir`: 入力ディレクトリ。既定値は `test-data`。
- `--output-dir`: 出力ディレクトリ。既定値は `analysis/output`。
- `--provider`: `azure-openai` または `foundry`。
- `--deployment`: モデルデプロイ名。
- `--dry-run`: LLM を呼ばずに deterministic な文章で出力します。
- `--save-debug-files`: LLM 入力・生出力を保存します。シークレットは出力しません。
- `--candidate-limit`: 出力候補数の上限。
- `--verbose`: 詳細ログを出力します。

## 検証

検証では次を確認します。

- すべての `ProjectID` と `CustomerID` の関連キーが存在する。
- Markdown 文書数が案件 36 件、グローバル 2 件、合計 38 件である。
- Markdown Front Matter の `WinLoss`、`Industry`、`ProjectTheme` が `projects.csv` と一致する。
- `ProfitJPYMillion = RevenueJPYMillion - CostJPYMillion` が成立する。
- output の `rank`、`candidateId` が重複しない。
- スコアが 0 から 100 の範囲にある。
- output の `projectId` と `sourceId` が入力データに存在する。
- `expected-pattern-metrics.json` とコード計算値が一致する。

## 既知の制約

- LLM なしの `--dry-run` では、文章生成は deterministic なフォールバック文を使います。
- `--provider foundry` は設定項目のみ用意しており、モデル呼び出しは未実装です。
- Markdown 本文は全文を LLM 入力に渡さず、Front Matter と sourceId を根拠として使います。
- 既存 Web アプリへの読み込み接続は今回の範囲外です。

## 本番化する場合の拡張案

- Foundry Agent / Prompt Agent 実行へ切り替える。
- Azure AI Search へ投入済み文書の引用 URL を sourceId と連携する。
- 実行履歴を Blob Storage や Database に保存する。
- CI で `--dry-run` と `validation-report.json` を検証する。
- Executive Cockpit 側を `dashboard-data.json` 読み込みに差し替える。