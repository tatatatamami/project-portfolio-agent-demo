# Portfolio Analysis Workload

`test-data` 配下の複数案件データを読み込み、Service Portfolio Executive Cockpit が表示できる派生データ JSON を生成するローカル分析バッチです。DB、Web 画面、チャット画面は変更しません。

## 責任分担

Python コードは、案件数、受注率、売上、利益、平均利益率、平均工数削減率、根拠案件数、業種数、共通要件数、共通機能数、ICE 優先度を確定計算します。LLM は、経営層向け要約、事業化理由、再利用資産、標準化ギャップ、推奨事業モデル、リスク、90 日アクションなどの文章生成だけを担当します。

数値と ICE スコアは LLM に再計算させません。LLM が返した案件 ID、文書 ID、sourceId、数値は検証し、不一致がある場合は `dashboard-data.json` を出力しません。

LLM または dry-run fallback が生成する文章・判断項目には、根拠となる `sourceIds` を保持します。`executiveSummarySourceIds`、`businessReasonSourceIds`、`recommendedBusinessModel.sourceIds`、`standardizationGaps[].sourceIds`、`risks[].sourceIds`、`managementDecision.decisionSourceIds` に加え、成功要因、失敗要因、90日アクション、成功条件、中止・見直し条件は `{ "text": "...", "sourceIds": [...] }` 形式で出力します。sourceId が空、または入力データに存在しない場合は検証エラーになります。

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

## ICE 優先度

事業化候補の優先順位は ICE フレームワークで説明します。各軸は 0 から 100 の整数で、LLM の自由判断ではなく Python が実績値と明示基準から算出します。

```text
ICE Priority Score = 100 * ((Impact / 100) * (Confidence / 100) * (Ease / 100)) ** (1 / 3)
```

最終スコアは 0 から 100 に丸め、`scores.priority` と `ice.score` は同じ値にします。3 軸のうち 1 つが低い候補は、単純平均ではなく正規化幾何平均により総合スコアが下がります。

### Impact

事業化したときの効果を評価します。

- 受注率: 20%
- 平均利益率: 25%
- 受注売上規模: 20%
- 平均工数削減率: 20%
- 対象業種数: 15%

### Confidence

将来の成功保証ではなく、現時点のデータから判断できる分析確信度を評価します。候補内の充足率だけでなく、根拠案件数と業種数の絶対スケールも使うため、4案件で一貫していても満点にはなりません。

- 根拠案件数: 20%
- 業種多様性: 15%
- 根拠文書カバレッジ: 15%
- 共通パターン一貫性: 15%
- 成功実績の一貫性: 20%
- データ完全性: 15%

根拠案件数は 1案件=25、2案件=50、3案件=70、4案件=80、5案件=90、6案件以上=100 として評価します。業種多様性も絶対スケールで評価し、4業種は90点、5業種以上で100点です。

### Ease

標準サービス化、運用、販売に移しやすいかを評価します。

- 再利用準備度: 30%
- 標準化準備度: 25%
- ギャップ負荷: 20%
- Highリスク負荷: 15%
- 必要投資レベル: 10%

欠損値の扱いは軸ごとに変えています。Impact は利用可能な factor のウェイトを再正規化します。Confidence はデータ完全性で不確実性を表現します。Ease は情報不足そのものが実行リスクになるため、必要投資レベルなどが不明な場合は除外せず50点として扱います。

Ease は候補間の相対評価だけでなく、絶対的な負荷も見ます。標準化ギャップは1件ごとに35点、Highリスクは1件ごとに12.5点を減点します。また、Highリスクが4件以上ならEase上限70、8件以上なら上限55、標準化ギャップが1件以上なら上限65として、再利用準備度だけで過度に高得点にならないようにしています。

ランキングは `ice.score` の降順です。同点の場合は Impact、Confidence、Ease の順に高い候補を優先し、それでも同じ場合は `candidateId` 昇順で並べます。

旧来の補助スコアも Web 詳細に残していますが、優先順位の決定には使いません。

- `profitability`: 平均利益率と受注売上を重視します。
- `reusability`: 共通機能数、対象業種数、根拠案件数を重視します。
- `standardization`: 共通要件数と共通機能数を重視します。
- `recurringRevenue`: 工数削減率と運用・監視に転用しやすい共通機能数を重視します。
- `saasReadiness`: 共通要件数、共通機能数、失注件数による標準化難度を組み合わせます。
- `feasibility`: 失注件数と平均工数削減率から実行しやすさを見ます。
- `confidence`: 根拠案件数、根拠文書数、業種多様性、成功実績の一貫性を重視します。
- `priority`: ICE 優先度と同じ値です。

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

Azure AI Search に Markdown ナレッジを投入します。まず dry-run で文書数と schema を検証します。

```powershell
python analysis/upload_to_search.py --dry-run --verbose
```

実投入では `AZURE_SEARCH_ENDPOINT`、`AZURE_OPENAI_ENDPOINT`、`AZURE_OPENAI_EMBEDDING_DEPLOYMENT` を設定してください。`AZURE_AUTH_MODE=default-credential` の場合は `az login` 済みの Entra ID を使います。API Key を使う場合は `AZURE_SEARCH_API_KEY` と `AZURE_OPENAI_API_KEY` を `.env` に設定します。

```powershell
python analysis/upload_to_search.py --verbose
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

Search 投入スクリプトの主なオプション:

- `--schema`: Search index schema。既定値は `test-data/ai-search/index-schema.json`。
- `--index-name`: Search index 名。既定値は `project-knowledge-index`。
- `--embedding-deployment`: embedding 用 Azure OpenAI deployment 名。
- `--embedding-dimensions`: index の vector dimensions。既定値は `1536`。
- `--expected-count`: 投入対象文書数の期待値。既定値は `38`。
- `--dry-run`: Azure に接続せず、文書読み込みと schema 置換だけを検証します。

## 検証

検証では次を確認します。

- すべての `ProjectID` と `CustomerID` の関連キーが存在する。
- Markdown 文書数が案件 36 件、グローバル 2 件、合計 38 件である。
- Markdown Front Matter の `WinLoss`、`Industry`、`ProjectTheme` が `projects.csv` と一致する。
- `ProfitJPYMillion = RevenueJPYMillion - CostJPYMillion` が成立する。
- output の `rank`、`candidateId` が重複しない。
- スコアが 0 から 100 の範囲にある。
- `ice.score` が Impact、Confidence、Ease の正規化幾何平均と一致する。
- `scores.priority` が `ice.score` と一致する。
- 候補の並び順が ICE の降順とタイブレーク規則に一致する。
- LLM/fallback 生成項目の `sourceIds` が空でなく、入力データに存在する。
- output の `projectId` と `sourceId` が入力データに存在する。
- `expected-pattern-metrics.json` とコード計算値が一致する。

## 既知の制約

- LLM なしの `--dry-run` では、文章生成は deterministic なフォールバック文を使います。
- `--provider foundry` は設定項目のみ用意しており、モデル呼び出しは未実装です。
- Markdown 本文は全文を LLM 入力に渡さず、Front Matter と sourceId を根拠として使います。
- 既存 Web アプリは `dashboard-data.json` の ICE 情報を読み込み、ランキングと候補詳細に表示します。チャット機能、Azure AI Search、Foundry IQ、DB はこの workload では変更しません。

## 本番化する場合の拡張案

- Foundry Agent / Prompt Agent 実行へ切り替える。
- Azure AI Search へ投入済み文書の引用 URL を sourceId と連携する。
- 実行履歴を Blob Storage や Database に保存する。
- CI で `--dry-run` と `validation-report.json` を検証する。
- ICE factor の重みを設定ファイル化し、業務部門レビュー後に調整できるようにする。