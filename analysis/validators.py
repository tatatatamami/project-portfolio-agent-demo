from __future__ import annotations

from collections import Counter
from typing import Any

from models import LoadedData, ValidationIssue
from schemas import validate_required_shape


def validate_inputs(data: LoadedData) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    project_ids = {row["ProjectID"] for row in data.projects}
    customer_ids = {row["CustomerID"] for row in data.customers}

    _require_unique("ProjectID", [row["ProjectID"] for row in data.projects], issues)
    _require_unique("CustomerID", [row["CustomerID"] for row in data.customers], issues)
    for row in data.projects:
        if row["CustomerID"] not in customer_ids:
            issues.append(_error("FK_CUSTOMER", f"Unknown CustomerID {row['CustomerID']} in project {row['ProjectID']}"))
    for name, rows in [("financials", data.financials), ("requirements", data.requirements), ("risks", data.risks), ("features", data.features), ("outcomes", data.outcomes), ("proposals", data.proposals)]:
        for row in rows:
            if row["ProjectID"] not in project_ids:
                issues.append(_error("FK_PROJECT", f"Unknown ProjectID {row['ProjectID']} in {name}"))

    approved_requirements = [row for row in data.requirements if row["KnowledgeStatus"] == "Approved"]
    approved_risks = [row for row in data.risks if row["KnowledgeStatus"] == "Approved"]
    approved_features = [row for row in data.features if row["KnowledgeStatus"] == "Approved"]
    expected_counts = {"requirements": 72, "risks": 48, "features": 60}
    actual_counts = {"requirements": len(approved_requirements), "risks": len(approved_risks), "features": len(approved_features)}
    for key, expected in expected_counts.items():
        if actual_counts[key] != expected:
            issues.append(_error("APPROVED_COUNT", f"{key} approved count {actual_counts[key]} != {expected}"))

    case_docs = [doc for doc in data.documents if doc["metadata"].get("projectId") and doc["metadata"].get("projectId") != "GLOBAL"]
    global_docs = [doc for doc in data.documents if doc["metadata"].get("projectId") == "GLOBAL" or not doc["metadata"].get("projectId")]
    if len(case_docs) != 36 or len(global_docs) != 2 or len(data.documents) != 38:
        issues.append(_error("DOCUMENT_COUNT", f"Document count mismatch: case={len(case_docs)}, global={len(global_docs)}, total={len(data.documents)}"))
    for doc in case_docs:
        metadata = doc["metadata"]
        project_id = metadata.get("projectId")
        if project_id not in project_ids:
            issues.append(_error("DOC_PROJECT", f"Document {doc['sourceId']} references unknown project {project_id}"))
        project = next((row for row in data.projects if row["ProjectID"] == project_id), None)
        if project and (metadata.get("winLoss") != project["WinLoss"] or metadata.get("industry") != project["Industry"] or metadata.get("projectTheme") != project["ProjectTheme"]):
            issues.append(_error("DOC_METADATA", f"Document {doc['sourceId']} metadata does not match projects.csv"))

    for row in data.financials:
        revenue = _number(row["RevenueJPYMillion"])
        cost = _number(row["CostJPYMillion"])
        profit = _number(row["ProfitJPYMillion"])
        if round(revenue - cost, 1) != round(profit, 1):
            issues.append(_error("FINANCIAL_PROFIT", f"Profit mismatch for {row['ProjectID']}"))
    return issues


def validate_dashboard(data: LoadedData, calculated: dict[str, Any], dashboard: dict[str, Any]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for message in validate_required_shape(dashboard):
        issues.append(_error("SCHEMA", message))

    ranks = [candidate["rank"] for candidate in dashboard.get("candidates", [])]
    candidate_ids = [candidate["candidateId"] for candidate in dashboard.get("candidates", [])]
    _require_unique("rank", ranks, issues)
    _require_unique("candidateId", candidate_ids, issues)
    known_source_ids = _known_source_ids(data)
    known_project_ids = {row["ProjectID"] for row in data.projects}

    for candidate in dashboard.get("candidates", []):
        for score_name, score in candidate.get("scores", {}).items():
            if not isinstance(score, int) or score < 0 or score > 100:
                issues.append(_error("SCORE_RANGE", f"{candidate['candidateId']} score {score_name} is out of range"))
        for project in candidate.get("supportingProjects", []):
            if project.get("projectId") not in known_project_ids:
                issues.append(_error("PROJECT_ID", f"Unknown projectId in output: {project.get('projectId')}"))
            _validate_sources(project.get("sourceIds", []), known_source_ids, issues, project.get("projectId", "supportingProject"))
        for asset in candidate.get("reusableAssets", []):
            _validate_sources(asset.get("sourceIds", []), known_source_ids, issues, asset.get("name", "asset"))
        for risk in candidate.get("risks", []):
            _validate_sources(risk.get("sourceIds", []), known_source_ids, issues, risk.get("name", "risk"))

    expected_by_theme = data.expected_metrics
    calculated_by_theme = {candidate["theme"]: candidate for candidate in calculated["candidates"]}
    for theme, expected in expected_by_theme.items():
        if theme.startswith("_"):
            continue
        actual = calculated_by_theme.get(theme)
        if not actual:
            issues.append(_error("EXPECTED_THEME", f"Missing calculated theme: {theme}"))
            continue
        metric_map = {
            "projectCount": actual["metrics"]["supportingProjectCount"],
            "wonCount": len([project for project in actual["supportingProjects"] if project["projectId"] in expected.get("wonProjectIds", [])]),
            "winRatePct": actual["metrics"]["winRate"],
            "averageWonProfitMarginPct": actual["metrics"]["averageMarginRate"],
            "averageWonEffortReductionPct": actual["metrics"]["averageEffortReductionRate"],
            "totalWonRevenueJPYMillion": actual["metrics"]["totalWonRevenueJPYMillion"],
            "totalWonProfitJPYMillion": actual["metrics"]["totalWonProfitJPYMillion"],
            "lostBidCostJPYMillion": actual["metrics"]["lostBidCostJPYMillion"],
        }
        for key, actual_value in metric_map.items():
            expected_value = expected.get(key)
            if expected_value is not None and actual_value != expected_value:
                issues.append(_error("EXPECTED_METRIC", f"{theme}.{key}: {actual_value} != {expected_value}"))
    return issues


def build_validation_report(input_issues: list[ValidationIssue], output_issues: list[ValidationIssue]) -> dict[str, Any]:
    issues = input_issues + output_issues
    return {
        "status": "passed" if not issues else "failed",
        "issueCount": len(issues),
        "issues": [issue.__dict__ for issue in issues],
    }


def _known_source_ids(data: LoadedData) -> set[str]:
    ids = {doc["sourceId"] for doc in data.documents}
    for rows, key in [(data.requirements, "RequirementID"), (data.risks, "RiskID"), (data.features, "FeatureID"), (data.outcomes, "OutcomeID"), (data.proposals, "ProposalID")]:
        ids.update(row[key] for row in rows)
    return ids


def _validate_sources(source_ids: list[str], known_source_ids: set[str], issues: list[ValidationIssue], owner: str) -> None:
    for source_id in source_ids:
        if source_id not in known_source_ids:
            issues.append(_error("SOURCE_ID", f"Unknown sourceId {source_id} in {owner}"))


def _require_unique(name: str, values: list[Any], issues: list[ValidationIssue]) -> None:
    duplicates = [value for value, count in Counter(values).items() if count > 1]
    if duplicates:
        issues.append(_error("DUPLICATE", f"Duplicate {name}: {duplicates}"))


def _number(value: str | None) -> float:
    if value in (None, "", "null"):
        return 0.0
    return float(value)


def _error(code: str, message: str) -> ValidationIssue:
    return ValidationIssue(severity="error", code=code, message=message)
