# Azure SQL MCP integration for service-portfolio-chat-agent-vnext

This demo uses Azure SQL for structured portfolio facts and Azure AI Search for unstructured document evidence.

## Azure resources

- Resource group: `rg-ti-demo-ai-agents-swc`
- Region: `swedencentral`
- SQL server: `ti-demo-ai-agents-swc-sql.database.windows.net`
- SQL database: `service-portfolio-db`
- Authentication: Microsoft Entra ID only
- Demo firewall rule: `AllowCurrentClientIpForDemoSeed`
- Target Foundry agent: `service-portfolio-chat-agent-vnext`
- Target agent managed identity principal ID: `cc7494ee-7bdb-4a1f-b08a-5704ae980641`
- Azure AI Search service: `ti-demo-ai-agents-swc-search`
- Azure AI Search connection: `video-scene-aisearch`
- Azure AI Search index: `project-knowledge-index`
- SQL MCP Container App: `ca-portfolio-sql-mcp`
- SQL MCP endpoint: `https://ca-portfolio-sql-mcp.lemonbeach-318498f8.swedencentral.azurecontainerapps.io/mcp`
- SQL MCP Container App identity principal ID: `95b9a70d-18c7-4a70-97f0-df072531a624`

## Seed data

```powershell
Set-Location "$env:TEMP\project-portfolio-agent-demo-tmp"
python analysis/load_to_sql.py --dry-run --verbose
python analysis/load_to_sql.py --verbose
```

The loader uses Azure CLI or DefaultAzureCredential tokens for `https://database.windows.net/.default`.

Expected high-level counts:

- `Projects`: 12
- `ServiceCandidates`: 3
- `Documents`: 38
- `Requirements`: 84
- `Features`: 72
- `Risks`: 60

Grant read-only access to the target agent identity:

```powershell
Set-Location "$env:TEMP\project-portfolio-agent-demo-tmp"
python analysis/grant_sql_agent_reader.py
```

This creates the contained external user `service-portfolio-chat-agent-vnext` and adds it to `db_datareader`.

## MCP tool configuration in Foundry portal

Add a custom **Model Context Protocol (MCP)** tool to `service-portfolio-chat-agent-vnext`.

Use these connection values:

- Name / server label: `portfolio-sql-mcp`
- Remote MCP server endpoint: `https://ca-portfolio-sql-mcp.lemonbeach-318498f8.swedencentral.azurecontainerapps.io/mcp`
- Authentication: `Unauthenticated`

The SQL MCP Server itself connects to Azure SQL by using the Container App managed identity. That identity is granted `db_datareader` in `service-portfolio-db`.

Prefer read-only access for the tool principal. The agent should query views rather than free-form base tables when possible.

Recommended views for the agent:

- `dbo.vTopCandidates`
- `dbo.vCandidateIceBreakdown`
- `dbo.vCandidateEvidenceProjects`
- `dbo.vCandidateSaasGaps`
- `dbo.vCandidate90DayDecisions`

Recommended allowed MCP tools:

- `describe_entities`
- `read_records`
- `aggregate_records`

Do not allow write tools for this demo (`create_record`, `update_record`, `delete_record`). The database permissions are read-only, but limiting allowed tools keeps the agent behavior clear.

## Automated Foundry agent update

The current demo also includes a REST update helper for the new Foundry Agents API:

```powershell
Set-Location "$env:TEMP\project-portfolio-agent-demo-tmp"
python analysis/update_foundry_vnext_mcp.py
```

The script:

- reads the known-good `service-portfolio-chat-agent-vnext` version 2 definition,
- appends SQL MCP usage instructions,
- adds the `portfolio-sql-mcp` remote MCP tool,
- adds the Azure AI Search tool for `project-knowledge-index`,
- creates a new agent version through `POST /agents/service-portfolio-chat-agent-vnext/versions?api-version=2025-05-15-preview`.

Validated latest version after the MCP + Azure AI Search update and natural-language routing instruction patch: `service-portfolio-chat-agent-vnext:8`.

The tool payload is normalized by Foundry to this shape:

```json
{
	"type": "mcp",
	"server_label": "portfolio-sql-mcp",
	"server_url": "https://ca-portfolio-sql-mcp.lemonbeach-318498f8.swedencentral.azurecontainerapps.io/mcp",
	"allowed_tools": {
		"tool_names": [
			"describe_entities",
			"read_records",
			"aggregate_records"
		]
	},
	"require_approval": "never"
}
```

The Azure AI Search tool payload uses the vnext REST shape below. The index contains 38 approved project knowledge documents.

```json
{
	"type": "azure_ai_search",
	"azure_ai_search": {
		"indexes": [
			{
				"project_connection_id": "/subscriptions/c101003f-208d-4d2e-95f2-6de6851774fa/resourceGroups/rg-ti-demo-ai-agents-swc/providers/Microsoft.CognitiveServices/accounts/ti-demo-ai-agents-swc-foundry/projects/proj-default/connections/video-scene-aisearch",
				"index_name": "project-knowledge-index",
				"query_type": "simple",
				"top_k": 5,
				"filter": "knowledgeStatus eq 'Approved'"
			}
		]
	}
}
```

## Agent instruction patch

Add this to the agent instructions:

```text
Use Azure SQL MCP Server for structured portfolio facts: candidate ranking, ICE breakdown, candidate comparison, SaaS gaps, evidence project lists, and 90-day management decisions.
Use Azure AI Search for document text, source evidence, and sourceId-level citations.
Do not execute arbitrary SQL or expose raw SQL to users. Prefer the curated SQL views:
dbo.vTopCandidates, dbo.vCandidateIceBreakdown, dbo.vCandidateEvidenceProjects, dbo.vCandidateSaasGaps, dbo.vCandidate90DayDecisions.
Do not invent forecasts, market size estimates, official investment decisions, unsupported SaaS recommendations, projects, or documents.
When a user asks a condition-change question, label the result as 仮の評価条件によるシミュレーション and do not silently change the official ICE score.
```

## Smoke tests

Ask `service-portfolio-chat-agent-vnext`:

1. `なぜこの候補が最優先なのですか`
2. `ICEスコアの内訳を説明してください`
3. `1位と2位を比較してください`
4. `SaaS化するために不足している要素は何ですか`
5. `次の90日で何を決めるべきですか`
6. `根拠案件を教えてください`

Expected behavior:

- SQL MCP is used for rankings, metrics, and comparisons.
- Azure AI Search is used for document evidence.
- The agent does not run or describe arbitrary SQL.

Validated Responses API smoke test:

- Request used `agent_reference` with `service-portfolio-chat-agent-vnext`.
- Response status: `completed`.
- Agent version used: `8`.
- MCP calls completed: `describe_entities`, `read_records`.
- Azure AI Search calls completed: `azure_ai_search_call`, `azure_ai_search_call_output`.

Validated natural-language prompts without explicit tool names:

- `1位と2位の候補を比較してください。` uses SQL MCP.
- `1位候補をSaaS化するために不足している要素は何ですか。` uses SQL MCP.
- `P001のRFPや提案概要、振り返り文書を検索して要点を教えてください。` uses Azure AI Search.

For mixed questions that need both structured metrics and document evidence, the most reliable prompt shape is to mention the evidence source category, for example `数値とRFP/提案概要/振り返り文書の両方から説明してください。`

## Current application boundary

The local Blazor app currently calls the classic Foundry Assistants API (`/assistants`, `/threads`, `/runs`).
`service-portfolio-chat-agent-vnext` is visible through the new Foundry Agents API (`/agents?api-version=2025-05-15-preview`) and its endpoint advertises the `responses` protocol.

Until the application client is migrated to the new responses protocol, keep `src/ServicePortfolio.Dashboard/appsettings.Development.json` pointed at the existing classic assistant. Use the Foundry portal playground to test the Azure SQL MCP tool on `service-portfolio-chat-agent-vnext`.
