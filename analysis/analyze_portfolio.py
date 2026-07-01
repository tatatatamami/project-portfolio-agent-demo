from __future__ import annotations

import json
import logging
import sys
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from config import parse_args
from data_loader import load_portfolio_data
from llm_client import PortfolioAnalysisLlmClient, load_prompt
from metrics import build_dashboard_candidate, build_metrics
from validators import build_validation_report, validate_dashboard, validate_inputs


PROMPT_VERSION = "v1"


def main() -> int:
    config = parse_args()
    logging.basicConfig(level=logging.DEBUG if config.verbose else logging.INFO, format="%(levelname)s %(message)s")
    logging.info("Starting Portfolio Analysis Workload")
    logging.info("Input directory: %s", config.input_dir)
    data = load_portfolio_data(config.input_dir)
    logging.info("Loaded projects=%s documents=%s", len(data.projects), len(data.documents))

    input_issues = validate_inputs(data)
    calculated = build_metrics(data, config.candidate_limit)
    logging.info("Calculated candidates=%s", len(calculated["candidates"]))

    llm_call_count = 0
    llm_inputs = []
    llm_raw_outputs = []
    prompt = load_prompt()
    client = None if config.dry_run else PortfolioAnalysisLlmClient(config)
    dashboard_candidates = []
    for candidate_summary in calculated["candidates"]:
        llm_payload = None
        if client:
            llm_input = _candidate_llm_input(candidate_summary)
            llm_inputs.append(llm_input)
            llm_payload = client.analyze_candidate(prompt, llm_input)
            llm_raw_outputs.append({"candidateId": candidate_summary["candidateId"], "output": llm_payload})
            llm_call_count += 1
        dashboard_candidates.append(build_dashboard_candidate(candidate_summary, llm_payload))

    generated_at = datetime.now(UTC).isoformat()
    dashboard_data = {
        "analysisRun": {
            "runId": str(uuid4()),
            "status": "completed" if not input_issues else "completed_with_validation_errors",
            "generatedAt": generated_at,
            "sourceProjectCount": calculated["source"]["projectCount"],
            "modelProvider": "dry-run" if config.dry_run else config.provider,
            "modelDeployment": config.deployment or "none",
            "promptVersion": PROMPT_VERSION,
        },
        "dashboardSummary": calculated["dashboardSummary"],
        "candidates": dashboard_candidates,
    }
    output_issues = validate_dashboard(data, calculated, dashboard_data)
    validation_report = build_validation_report(input_issues, output_issues)
    analysis_run = {
        "runId": dashboard_data["analysisRun"]["runId"],
        "status": validation_report["status"],
        "generatedAt": generated_at,
        "inputDir": str(config.input_dir),
        "outputDir": str(config.output_dir),
        "modelProvider": dashboard_data["analysisRun"]["modelProvider"],
        "modelDeployment": dashboard_data["analysisRun"]["modelDeployment"],
        "llmCallCount": llm_call_count,
        "candidateCount": len(dashboard_candidates),
        "source": calculated["source"],
        "validation": {"status": validation_report["status"], "issueCount": validation_report["issueCount"]},
    }

    config.output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(config.output_dir / "validation-report.json", validation_report)
    _write_json(config.output_dir / "analysis-run.json", analysis_run)
    if validation_report["status"] == "passed":
        _write_json(config.output_dir / "dashboard-data.json", dashboard_data)
    else:
        logging.error("Validation failed; dashboard-data.json was not written")
    if config.save_debug_files:
        _write_json(config.output_dir / "llm-input.json", llm_inputs or [_candidate_llm_input(item) for item in calculated["candidates"]])
        _write_json(config.output_dir / "llm-raw-output.json", llm_raw_outputs)

    logging.info("Validation status: %s", validation_report["status"])
    logging.info("Output directory: %s", config.output_dir)
    return 0 if validation_report["status"] == "passed" else 2


def _candidate_llm_input(candidate_summary: dict) -> dict:
    return {
        "candidateId": candidate_summary["candidateId"],
        "name": candidate_summary["name"],
        "theme": candidate_summary["theme"],
        "metrics": candidate_summary["metrics"],
        "scores": candidate_summary["scores"],
        "commonRequirements": candidate_summary["commonRequirements"],
        "commonFeatures": candidate_summary["commonFeatures"],
        "commonRisks": candidate_summary["commonRisks"],
        "supportingProjects": candidate_summary["supportingProjects"],
        "sourceIds": candidate_summary["sourceIds"],
    }


def _write_json(path: Path, value: dict | list) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
