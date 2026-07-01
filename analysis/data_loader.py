from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from models import LoadedData


CSV_FILES = {
    "customers": "customers.csv",
    "projects": "projects.csv",
    "opportunities": "opportunities.csv",
    "proposals": "proposals.csv",
    "requirements": "requirements.csv",
    "risks": "risks.csv",
    "features": "features.csv",
    "financials": "project-financials.csv",
    "outcomes": "business-outcomes.csv",
}


def load_portfolio_data(input_dir: Path) -> LoadedData:
    fabric_dir = input_dir / "fabric"
    expected_dir = input_dir / "expected"
    if not fabric_dir.exists():
        raise FileNotFoundError(f"Missing input directory: {fabric_dir}")

    rows = {name: _read_csv(fabric_dir / filename) for name, filename in CSV_FILES.items()}
    documents = _read_documents(input_dir)
    expected_metrics = _read_json(expected_dir / "expected-pattern-metrics.json")
    validation_rules = _read_json(expected_dir / "validation-rules.json")

    return LoadedData(
        customers=rows["customers"],
        projects=rows["projects"],
        opportunities=rows["opportunities"],
        proposals=rows["proposals"],
        requirements=rows["requirements"],
        risks=rows["risks"],
        features=rows["features"],
        financials=rows["financials"],
        outcomes=rows["outcomes"],
        documents=documents,
        expected_metrics=expected_metrics,
        validation_rules=validation_rules,
    )


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(f"Missing CSV file: {path}")
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing JSON file: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON file: {path}: {exc}") from exc


def _read_documents(input_dir: Path) -> list[dict[str, Any]]:
    documents: list[dict[str, Any]] = []
    for path in sorted((input_dir / "ai-search" / "documents").glob("**/*.md")):
        documents.append(_read_markdown(path, input_dir))
    for path in sorted((input_dir / "ai-search" / "global").glob("*.md")):
        documents.append(_read_markdown(path, input_dir))
    return documents


def _read_markdown(path: Path, input_dir: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8-sig")
    metadata: dict[str, Any] = {}
    body = text
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            metadata = _parse_front_matter(parts[1])
            body = parts[2].strip()
    document_id = metadata.get("documentId") or path.stem
    return {
        "sourceId": str(document_id),
        "path": str(path.relative_to(input_dir)).replace("\\", "/"),
        "metadata": metadata,
        "content": body,
    }


def _parse_front_matter(raw: str) -> dict[str, Any]:
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
