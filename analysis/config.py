from __future__ import annotations

import argparse
import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AnalysisConfig:
    input_dir: Path
    output_dir: Path
    provider: str
    deployment: str | None
    dry_run: bool
    save_debug_files: bool
    candidate_limit: int | None
    verbose: bool
    temperature: float
    azure_auth_mode: str
    azure_openai_endpoint: str | None
    azure_openai_api_key: str | None
    azure_openai_api_version: str
    azure_foundry_endpoint: str | None


def load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def parse_args() -> AnalysisConfig:
    load_dotenv(Path(".env"))
    parser = argparse.ArgumentParser(description="Generate Service Portfolio Executive Cockpit analysis data.")
    parser.add_argument("--input-dir", default="test-data")
    parser.add_argument("--output-dir", default=os.getenv("ANALYSIS_OUTPUT_DIR", "analysis/output"))
    parser.add_argument("--provider", default=os.getenv("ANALYSIS_MODEL_PROVIDER", "azure-openai"), choices=["azure-openai", "foundry"])
    parser.add_argument("--deployment", default=os.getenv("AZURE_OPENAI_DEPLOYMENT") or os.getenv("AZURE_FOUNDRY_MODEL_DEPLOYMENT"))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--save-debug-files", action="store_true")
    parser.add_argument("--candidate-limit", type=int, default=None)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    return AnalysisConfig(
        input_dir=Path(args.input_dir),
        output_dir=Path(args.output_dir),
        provider=args.provider,
        deployment=args.deployment,
        dry_run=args.dry_run,
        save_debug_files=args.save_debug_files,
        candidate_limit=args.candidate_limit,
        verbose=args.verbose,
        temperature=float(os.getenv("ANALYSIS_TEMPERATURE", "0.1")),
        azure_auth_mode=os.getenv("AZURE_AUTH_MODE", "default-credential"),
        azure_openai_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT") or None,
        azure_openai_api_key=os.getenv("AZURE_OPENAI_API_KEY") or None,
        azure_openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21"),
        azure_foundry_endpoint=os.getenv("AZURE_FOUNDRY_ENDPOINT") or None,
    )
