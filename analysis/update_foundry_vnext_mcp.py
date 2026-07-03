from __future__ import annotations

import json
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from typing import Any

PROJECT_ENDPOINT = "https://ti-demo-ai-agents-swc-foundry.services.ai.azure.com/api/projects/proj-default"
API_VERSION = "2025-05-15-preview"
AGENT_NAME = "service-portfolio-chat-agent-vnext"
MCP_URL = "https://ca-portfolio-sql-mcp.lemonbeach-318498f8.swedencentral.azurecontainerapps.io/mcp"
MCP_LABEL = "portfolio-sql-mcp"
ALLOWED_TOOLS = ["describe_entities", "read_records", "aggregate_records"]
AI_SEARCH_CONNECTION_ID = "/subscriptions/c101003f-208d-4d2e-95f2-6de6851774fa/resourceGroups/rg-ti-demo-ai-agents-swc/providers/Microsoft.CognitiveServices/accounts/ti-demo-ai-agents-swc-foundry/projects/proj-default/connections/video-scene-aisearch"
AI_SEARCH_INDEX_NAME = "project-knowledge-index"


def main() -> None:
    token = get_token()
    source_version = request_json("GET", f"{PROJECT_ENDPOINT}/agents/{AGENT_NAME}/versions/2?api-version={API_VERSION}", token)
    definition = dict(source_version["definition"])
    definition["instructions"] = definition["instructions"] + """

Use the portfolio-sql-mcp MCP server for structured portfolio facts: candidate ranking, ICE breakdown, candidate comparison, SaaS gaps, evidence project lists, and 90-day management decisions.
Always call describe_entities before using read_records or aggregate_records.
Prefer these entities when answering management questions: TopCandidates, CandidateIceBreakdown, CandidateEvidenceProjects, CandidateSaasGaps, Candidate90DayDecisions.
Use read_records for row-level evidence and aggregate_records for counts or simple summaries.
Users do not need to name tools. When a user asks about 1位, 2位, 上位候補, 優先度, ICE, スコア, 比較, SaaS化, 不足要素, 根拠案件, or 90日で決めること, infer that they are asking about the Service Portfolio Executive Cockpit data and use portfolio-sql-mcp automatically.
Do not ask the user to rephrase common cockpit questions such as "1位と2位の候補を比較してください". Treat "1位" and "2位" as Rank 1 and Rank 2 in TopCandidates unless the user explicitly provides a different ranking context.
日本語の質問では、ユーザーがツール名を指定しなくても自律的にツールを選択してください。
「1位候補」「2位候補」「上位候補」「サービス化優先度」「優先度が高い理由」「数値」「ICE」「スコア」「SaaS化」「不足している要素」は、必ず portfolio-sql-mcp を使って確認してから回答してください。
「根拠文書」「文書根拠」「RFP」「提案概要」「振り返り」「設計判断」「背景」「教訓」「sourceId」は、必ず Azure AI Search を使って確認してから回答してください。
「数値と根拠文書の両方」「数値と文書の両方」「優先度が高い理由を数値と根拠文書から」と聞かれた場合は、必ず portfolio-sql-mcp と Azure AI Search の両方を使ってください。
これらの質問では「質問を言い換えてください」「どの候補か指定してください」と返さず、Rank 1を1位候補として扱って回答してください。
Field names in SQL MCP are case-sensitive. Use these exact field names:
- TopCandidates: Rank, CandidateID, Name, IceScore, WinRate, AverageMarginRate, WonRevenue, SupportingProjectCount, IndustryCount, SaasReadiness, CurrentBusinessModel, NextBusinessModel, FutureBusinessModel
- CandidateIceBreakdown: Rank, CandidateID, CandidateName, IceScore, AxisName, AxisScore, Summary, FactorOrder, FactorName, FactorValue, Contribution
- CandidateEvidenceProjects: Rank, CandidateID, CandidateName, ProjectID, ProjectName, Industry, EvidenceSummary, SourceIDs
- CandidateSaasGaps: Rank, CandidateID, CandidateName, GapOrder, Category, CurrentState, TargetState, Priority, Effort, Dependency, SourceIDs
- Candidate90DayDecisions: Rank, CandidateID, CandidateName, Decision, InvestmentLevel, TimeHorizon, ItemType, ItemOrder, ItemText, SourceIDs
Use Azure AI Search or provided source context for document text and sourceId-level citations.
Use the Azure AI Search tool for unstructured document evidence, sourceId details, proposal summaries, RFP context, bid reviews, retrospectives, design decisions, lessons learned, risks, and reusable patterns.
When the user asks about evidence, background, lessons learned, why a project succeeded or failed, or details behind a sourceId, use Azure AI Search in addition to portfolio-sql-mcp.
When the user asks for both 数値 and 根拠文書, use both tools: portfolio-sql-mcp for scores and structured metrics, then Azure AI Search for document evidence. Do this even when the user does not mention either tool by name.
Search only approved knowledge. Treat SQL MCP as the source for structured metrics and Azure AI Search as the source for document text and qualitative evidence.
Do not use write tools. Do not execute arbitrary SQL or expose raw SQL to users.
"""
    tools = [tool for tool in definition.get("tools", []) if tool.get("server_label") != MCP_LABEL and tool.get("type") != "azure_ai_search"]
    tools.append(
        {
            "type": "mcp",
            "server_label": MCP_LABEL,
            "server_url": MCP_URL,
            "require_approval": "never",
            "allowed_tools": ALLOWED_TOOLS,
        }
    )
    tools.append(
        {
            "type": "azure_ai_search",
            "azure_ai_search": {
                "indexes": [
                    {
                        "project_connection_id": AI_SEARCH_CONNECTION_ID,
                        "index_name": AI_SEARCH_INDEX_NAME,
                        "query_type": "simple",
                        "filter": "knowledgeStatus eq 'Approved'",
                        "top_k": 5,
                    }
                ]
            },
        }
    )
    definition["tools"] = tools

    body = {
        "description": "Service portfolio chat agent with Azure SQL MCP Server for structured portfolio facts.",
        "definition": definition,
    }

    try:
        updated = request_json("POST", f"{PROJECT_ENDPOINT}/agents/{AGENT_NAME}/versions?api-version={API_VERSION}", token, body)
    except urllib.error.HTTPError as exc:
        print_error(exc)
        sys.exit(1)

    print(json.dumps({"id": updated.get("id"), "name": updated.get("name"), "version": updated.get("version")}, ensure_ascii=False, indent=2))

    refreshed = request_json("GET", f"{PROJECT_ENDPOINT}/agents/{AGENT_NAME}?api-version={API_VERSION}", token)
    latest_tools = refreshed["versions"]["latest"]["definition"].get("tools", [])
    print(json.dumps(latest_tools, ensure_ascii=False, indent=2))


def get_token() -> str:
    az_command = shutil.which("az") or shutil.which("az.cmd") or "az"
    result = subprocess.run(
        [az_command, "account", "get-access-token", "--scope", "https://ai.azure.com/.default", "--query", "accessToken", "-o", "tsv"],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def request_json(method: str, url: str, token: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
    data = None if body is None else json.dumps(body).encode("utf-8")
    request = urllib.request.Request(url, data=data, method=method)
    request.add_header("Authorization", f"Bearer {token}")
    request.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(request, timeout=120) as response:
        return json.loads(response.read().decode("utf-8"))


def print_error(exc: urllib.error.HTTPError) -> None:
    body = exc.read().decode("utf-8", errors="replace")
    print(f"HTTP {exc.code}: {exc.reason}")
    print(body)


if __name__ == "__main__":
    main()
