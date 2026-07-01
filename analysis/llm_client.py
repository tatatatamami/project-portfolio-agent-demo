from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Any

from config import AnalysisConfig
from schemas import LLM_RESPONSE_JSON_SCHEMA


class PortfolioAnalysisLlmClient:
    def __init__(self, config: AnalysisConfig) -> None:
        self._config = config

    def analyze_candidate(self, prompt_template: str, candidate_input: dict[str, Any]) -> dict[str, Any]:
        if self._config.provider != "azure-openai":
            raise NotImplementedError("Foundry provider is configured, but local Foundry chat invocation is not implemented yet.")
        client = self._build_azure_openai_client()
        messages = [
            {"role": "system", "content": prompt_template},
            {"role": "user", "content": json.dumps(candidate_input, ensure_ascii=False)},
        ]
        last_error: Exception | None = None
        for attempt in range(5):
            try:
                logging.info("Calling Azure OpenAI for candidate %s", candidate_input.get("candidateId"))
                response = client.chat.completions.create(
                    model=self._config.deployment,
                    messages=messages,
                    temperature=self._config.temperature,
                    response_format=LLM_RESPONSE_JSON_SCHEMA,
                )
                content = response.choices[0].message.content or "{}"
                return json.loads(content)
            except Exception as exc:  # pragma: no cover - depends on Azure availability
                last_error = exc
                wait_seconds = min(2**attempt, 16)
                logging.warning("Model call failed on attempt %s: %s", attempt + 1, exc)
                time.sleep(wait_seconds)
        raise RuntimeError(f"Model call failed after retries: {last_error}")

    def _build_azure_openai_client(self):
        try:
            from openai import AzureOpenAI
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError("openai package is required. Run: pip install -r analysis/requirements.txt") from exc
        if not self._config.deployment:
            raise RuntimeError("AZURE_OPENAI_DEPLOYMENT or --deployment is required for model calls.")
        if not self._config.azure_openai_endpoint:
            raise RuntimeError("AZURE_OPENAI_ENDPOINT is required for Azure OpenAI model calls.")
        if self._config.azure_auth_mode == "api-key":
            if not self._config.azure_openai_api_key:
                raise RuntimeError("AZURE_OPENAI_API_KEY is required when AZURE_AUTH_MODE=api-key.")
            return AzureOpenAI(
                azure_endpoint=self._config.azure_openai_endpoint,
                api_key=self._config.azure_openai_api_key,
                api_version=self._config.azure_openai_api_version,
            )
        try:
            from azure.identity import DefaultAzureCredential, get_bearer_token_provider
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError("azure-identity package is required for DefaultAzureCredential.") from exc
        token_provider = get_bearer_token_provider(DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default")
        return AzureOpenAI(
            azure_endpoint=self._config.azure_openai_endpoint,
            azure_ad_token_provider=token_provider,
            api_version=self._config.azure_openai_api_version,
        )


def load_prompt() -> str:
    return (Path(__file__).parent / "prompts" / "portfolio_candidate_analysis.md").read_text(encoding="utf-8")
