from __future__ import annotations

import json
import shutil
import subprocess
import sys
import urllib.error
import urllib.request

PROJECT_ENDPOINT = "https://ti-demo-ai-agents-swc-foundry.services.ai.azure.com/api/projects/proj-default"
AGENT_NAME = "service-portfolio-chat-agent-vnext"

QUESTIONS = [
    "portfolio-sql-mcpを使って、TopCandidatesから1位と2位の候補名とIceScoreを取得して比較してください。",
    "portfolio-sql-mcpを使って、1位候補のICEスコアの内訳をImpact、Confidence、Easeに分けて説明してください。",
    "portfolio-sql-mcpを使って、1位候補をSaaS化するために不足している要素を教えてください。",
    "portfolio-sql-mcpを使って、次の90日で決めるべき事項を教えてください。",
]


def main() -> None:
    token = get_token()
    for index, question in enumerate(QUESTIONS, start=1):
        print(f"\n===== TEST {index} =====")
        print(f"Q: {question}")
        response = call_agent(token, question)
        print(f"status: {response.get('status')}")
        print("tools:")
        for item in response.get("output", []):
            item_type = item.get("type")
            if item_type in {"mcp_list_tools", "mcp_call"}:
                print(f"- {item_type}: server={item.get('server_label')} name={item.get('name')} status={item.get('status')}")
        print("answer:")
        print(extract_answer(response))


def get_token() -> str:
    az_command = shutil.which("az") or shutil.which("az.cmd") or "az"
    result = subprocess.run(
        [az_command, "account", "get-access-token", "--scope", "https://ai.azure.com/.default", "--query", "accessToken", "-o", "tsv"],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def call_agent(token: str, question: str) -> dict:
    body = {
        "agent_reference": {"type": "agent_reference", "name": AGENT_NAME},
        "input": question,
    }
    request = urllib.request.Request(
        f"{PROJECT_ENDPOINT}/openai/v1/responses",
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        method="POST",
    )
    request.add_header("Authorization", f"Bearer {token}")
    request.add_header("Content-Type", "application/json; charset=utf-8")
    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        print(f"HTTP {exc.code}: {exc.reason}", file=sys.stderr)
        print(exc.read().decode("utf-8", errors="replace"), file=sys.stderr)
        raise


def extract_answer(response: dict) -> str:
    parts: list[str] = []
    for item in response.get("output", []):
        if item.get("type") != "message":
            continue
        for content in item.get("content", []):
            if content.get("type") == "output_text":
                parts.append(content.get("text", ""))
    return "\n".join(parts).strip()


if __name__ == "__main__":
    main()
