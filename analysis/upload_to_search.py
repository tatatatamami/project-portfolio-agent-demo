from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
from typing import Any
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from config import load_dotenv


DEFAULT_SEARCH_API_VERSION = "2024-07-01"
DEFAULT_INDEX_NAME = "project-knowledge-index"


def main() -> None:
    args = parse_args()
    load_dotenv(Path(args.env_file))

    input_dir = Path(args.input_dir)
    schema_path = Path(args.schema)
    documents = load_documents(input_dir, approved_only=not args.include_non_approved)
    schema = load_index_schema(schema_path, args.index_name, args.embedding_dimensions)

    if args.verbose or args.dry_run:
        print(f"Index name: {schema['name']}")
        print(f"Documents: {len(documents)}")
        print(f"Embedding dimensions: {args.embedding_dimensions}")

    if args.expected_count is not None and len(documents) != args.expected_count:
        raise RuntimeError(f"Expected {args.expected_count} documents, but loaded {len(documents)}.")

    if args.dry_run:
        return

    endpoint = required_env("AZURE_SEARCH_ENDPOINT").rstrip("/")
    api_version = os.getenv("AZURE_SEARCH_API_VERSION", DEFAULT_SEARCH_API_VERSION)
    auth_headers = build_search_auth_headers()

    print(f"Creating or updating Search index '{schema['name']}'...")
    send_search_request(
        "PUT",
        f"{endpoint}/indexes/{schema['name']}?api-version={api_version}",
        schema,
        auth_headers,
    )

    print("Generating embeddings...")
    embedder = AzureOpenAIEmbedder(args.embedding_deployment)
    upload_documents: list[dict[str, Any]] = []
    for document in documents:
        upload_document = dict(document)
        upload_document["@search.action"] = "upload"
        upload_document["contentVector"] = embedder.embed(f"{document['title']}\n\n{document['content']}")
        upload_documents.append(upload_document)

    print(f"Uploading {len(upload_documents)} documents...")
    send_search_request(
        "POST",
        f"{endpoint}/indexes/{schema['name']}/docs/index?api-version={api_version}",
        {"value": upload_documents},
        auth_headers,
    )

    print("Upload complete.")


def parse_args() -> argparse.Namespace:
    load_dotenv(Path(".env"))
    parser = argparse.ArgumentParser(description="Create Azure AI Search index and upload project knowledge Markdown documents.")
    parser.add_argument("--input-dir", default="test-data")
    parser.add_argument("--schema", default="test-data/ai-search/index-schema.json")
    parser.add_argument("--env-file", default=".env")
    parser.add_argument("--index-name", default=os.getenv("AZURE_SEARCH_INDEX_NAME", DEFAULT_INDEX_NAME))
    parser.add_argument("--embedding-deployment", default=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT"))
    parser.add_argument("--embedding-dimensions", type=int, default=int(os.getenv("AZURE_SEARCH_EMBEDDING_DIMENSIONS", "1536")))
    parser.add_argument("--expected-count", type=int, default=38)
    parser.add_argument("--include-non-approved", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    return parser.parse_args()


def load_documents(input_dir: Path, approved_only: bool) -> list[dict[str, Any]]:
    markdown_paths = [
        *sorted((input_dir / "ai-search" / "documents").glob("**/*.md")),
        *sorted((input_dir / "ai-search" / "global").glob("*.md")),
    ]
    documents = [read_markdown(path, input_dir) for path in markdown_paths]
    if approved_only:
        documents = [document for document in documents if document["knowledgeStatus"] == "Approved"]
    return documents


def read_markdown(path: Path, input_dir: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8-sig")
    metadata: dict[str, Any] = {}
    body = text.strip()
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            metadata = parse_front_matter(parts[1])
            body = parts[2].strip()

    document_id = required_metadata(metadata, "documentId", path)
    return {
        "id": sanitize_key(document_id),
        "documentId": document_id,
        "projectId": required_metadata(metadata, "projectId", path),
        "customerId": metadata.get("customerId", ""),
        "title": metadata.get("title", path.stem),
        "content": body,
        "documentType": metadata.get("documentType", "Unknown"),
        "industry": metadata.get("industry", "Unknown"),
        "projectTheme": metadata.get("projectTheme", "Unknown"),
        "winLoss": metadata.get("winLoss", "Unknown"),
        "knowledgeStatus": metadata.get("knowledgeStatus", "Unknown"),
        "confidentiality": metadata.get("confidentiality", "Internal"),
        "sourceDate": metadata.get("sourceDate"),
        "tags": metadata.get("tags", []),
        "sourceUrl": metadata.get("sourceUrl", str(path.relative_to(input_dir)).replace("\\", "/")),
    }


def parse_front_matter(raw: str) -> dict[str, Any]:
    result: dict[str, Any] = {}
    current_key: str | None = None
    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("-") and current_key:
            result.setdefault(current_key, []).append(stripped[1:].strip())
            continue
        if ":" in line:
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()
            current_key = key
            result[key] = [] if value == "" else value
    return result


def load_index_schema(path: Path, index_name: str, embedding_dimensions: int) -> dict[str, Any]:
    schema_text = path.read_text(encoding="utf-8-sig").replace('"${EMBEDDING_DIMENSIONS}"', str(embedding_dimensions))
    schema = json.loads(schema_text)
    schema["name"] = index_name
    schema.pop("_comment", None)
    normalize_semantic_schema(schema)
    return schema


def normalize_semantic_schema(schema: dict[str, Any]) -> None:
    for configuration in schema.get("semantic", {}).get("configurations", []):
        fields = configuration.get("prioritizedFields", {})
        if "contentFields" in fields:
            fields["prioritizedContentFields"] = fields.pop("contentFields")
        if "keywordsFields" in fields:
            fields["prioritizedKeywordsFields"] = fields.pop("keywordsFields")


def build_search_auth_headers() -> dict[str, str]:
    api_key = os.getenv("AZURE_SEARCH_API_KEY")
    if api_key:
        return {"api-key": api_key}

    token = get_default_credential_token("https://search.azure.com/.default")
    return {"Authorization": f"Bearer {token}"}


def send_search_request(method: str, url: str, body: dict[str, Any], headers: dict[str, str]) -> dict[str, Any]:
    request_headers = {"Content-Type": "application/json", **headers}
    request = Request(
        url,
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers=request_headers,
        method=method,
    )
    try:
        with urlopen(request) as response:
            content = response.read().decode("utf-8")
            return json.loads(content) if content else {}
    except HTTPError as exc:
        content = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Azure AI Search request failed with {exc.code}: {content}") from exc


def get_default_credential_token(scope: str) -> str:
    try:
        from azure.identity import DefaultAzureCredential
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("azure-identity package is required. Run: pip install -r analysis/requirements.txt") from exc
    return DefaultAzureCredential().get_token(scope).token


class AzureOpenAIEmbedder:
    def __init__(self, deployment: str | None) -> None:
        if not deployment:
            raise RuntimeError("AZURE_OPENAI_EMBEDDING_DEPLOYMENT or --embedding-deployment is required.")
        self._deployment = deployment
        self._client = self._build_client()

    def embed(self, text: str) -> list[float]:
        response = self._client.embeddings.create(model=self._deployment, input=text)
        return response.data[0].embedding

    @staticmethod
    def _build_client():
        try:
            from openai import AzureOpenAI
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError("openai package is required. Run: pip install -r analysis/requirements.txt") from exc

        endpoint = required_env("AZURE_OPENAI_ENDPOINT")
        api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21")
        if os.getenv("AZURE_AUTH_MODE") == "api-key":
            return AzureOpenAI(
                azure_endpoint=endpoint,
                api_key=required_env("AZURE_OPENAI_API_KEY"),
                api_version=api_version,
            )

        try:
            from azure.identity import DefaultAzureCredential, get_bearer_token_provider
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError("azure-identity package is required for DefaultAzureCredential.") from exc
        token_provider = get_bearer_token_provider(DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default")
        return AzureOpenAI(
            azure_endpoint=endpoint,
            azure_ad_token_provider=token_provider,
            api_version=api_version,
        )


def sanitize_key(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_=-]", "_", value)


def required_metadata(metadata: dict[str, Any], key: str, path: Path) -> str:
    value = metadata.get(key)
    if not isinstance(value, str) or not value.strip():
        raise RuntimeError(f"Missing required metadata '{key}' in {path}")
    return value


def required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"{name} is required.")
    return value


if __name__ == "__main__":
    main()
