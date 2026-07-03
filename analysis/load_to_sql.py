from __future__ import annotations

import argparse
import csv
import json
import struct
from pathlib import Path
from typing import Any, Iterable

import pyodbc
from azure.identity import AzureCliCredential, DefaultAzureCredential

SQL_COPT_SS_ACCESS_TOKEN = 1256
DATABASE_SCOPE = "https://database.windows.net/.default"

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

DELETE_ORDER = [
    "CandidateDecisionItems",
    "CandidateManagementDecisions",
    "CandidateRisks",
    "CandidateStandardizationGaps",
    "CandidateReusableAssets",
    "CandidateSupportingProjects",
    "CandidateIceFactors",
    "CandidateIceAxes",
    "CandidateMetrics",
    "CandidateScores",
    "ServiceCandidates",
    "Documents",
    "BusinessOutcomes",
    "Risks",
    "Features",
    "Requirements",
    "ProjectFinancials",
    "Proposals",
    "Opportunities",
    "Projects",
    "Customers",
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Load Service Portfolio demo data into Azure SQL Database.")
    parser.add_argument("--server", default="ti-demo-ai-agents-swc-sql.database.windows.net")
    parser.add_argument("--database", default="service-portfolio-db")
    parser.add_argument("--input-dir", type=Path, default=Path("test-data"))
    parser.add_argument("--dashboard", type=Path, default=Path("analysis/output/dashboard-data.json"))
    parser.add_argument("--driver", default="ODBC Driver 18 for SQL Server")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    input_dir = args.input_dir.resolve()
    dashboard_path = args.dashboard.resolve()
    data = load_sources(input_dir, dashboard_path)
    rows = build_rows(data)

    print_counts(rows)
    if args.dry_run:
        print("Dry run complete. No SQL changes were made.")
        return

    with connect(args.server, args.database, args.driver) as connection:
        connection.autocommit = False
        ensure_schema(connection)
        clear_tables(connection)
        insert_rows(connection, rows, args.verbose)
        connection.commit()

    print("Azure SQL load complete.")


def connect(server: str, database: str, driver: str) -> pyodbc.Connection:
    token = get_access_token()
    token_bytes = token.encode("utf-16-le")
    token_struct = struct.pack(f"<I{len(token_bytes)}s", len(token_bytes), token_bytes)
    connection_string = (
        f"Driver={{{driver}}};"
        f"Server=tcp:{server},1433;"
        f"Database={database};"
        "Encrypt=yes;"
        "TrustServerCertificate=no;"
        "Connection Timeout=60;"
    )
    return pyodbc.connect(connection_string, attrs_before={SQL_COPT_SS_ACCESS_TOKEN: token_struct})


def get_access_token() -> str:
    try:
        credential = AzureCliCredential()
        return credential.get_token(DATABASE_SCOPE).token
    except Exception:
        credential = DefaultAzureCredential(exclude_interactive_browser_credential=False)
        return credential.get_token(DATABASE_SCOPE).token


def load_sources(input_dir: Path, dashboard_path: Path) -> dict[str, Any]:
    fabric_dir = input_dir / "fabric"
    if not fabric_dir.exists():
        raise FileNotFoundError(f"Missing fabric directory: {fabric_dir}")
    if not dashboard_path.exists():
        raise FileNotFoundError(f"Missing dashboard JSON: {dashboard_path}")

    sources: dict[str, Any] = {name: read_csv(fabric_dir / filename) for name, filename in CSV_FILES.items()}
    sources["documents"] = read_documents(input_dir)
    sources["dashboard"] = json.loads(dashboard_path.read_text(encoding="utf-8-sig"))
    return sources


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def read_documents(input_dir: Path) -> list[dict[str, Any]]:
    documents: list[dict[str, Any]] = []
    for path in sorted((input_dir / "ai-search" / "documents").glob("**/*.md")):
        documents.append(read_markdown(path, input_dir))
    for path in sorted((input_dir / "ai-search" / "global").glob("*.md")):
        documents.append(read_markdown(path, input_dir))
    return documents


def read_markdown(path: Path, input_dir: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8-sig")
    metadata: dict[str, Any] = {}
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            metadata = parse_front_matter(parts[1])
    return {
        "sourceId": str(metadata.get("documentId") or path.stem),
        "projectId": metadata.get("projectId"),
        "documentType": metadata.get("documentType"),
        "title": metadata.get("title") or path.stem,
        "path": str(path.relative_to(input_dir)).replace("\\", "/"),
        "knowledgeStatus": metadata.get("knowledgeStatus"),
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


def build_rows(data: dict[str, Any]) -> dict[str, list[tuple[Any, ...]]]:
    dashboard = data["dashboard"]
    candidates = dashboard.get("candidates", [])

    rows: dict[str, list[tuple[Any, ...]]] = {
        "Customers": [
            (r.get("CustomerID"), r.get("CustomerName"), r.get("Industry"), r.get("Region"), r.get("Segment"), r.get("KnowledgeStatus"))
            for r in data["customers"]
        ],
        "Projects": [
            (r.get("ProjectID"), r.get("CustomerID"), r.get("ProjectName"), r.get("Industry"), r.get("ProjectTheme"), null_if_empty(r.get("StartDate")), null_if_empty(r.get("EndDate")), r.get("Status"), r.get("WinLoss"), r.get("KnowledgeStatus"))
            for r in data["projects"]
        ],
        "Opportunities": [
            (r.get("OpportunityID"), r.get("CustomerID"), r.get("ProjectID"), r.get("OpportunityName"), r.get("Stage"), decimal_or_none(r.get("AmountJPYMillion")), r.get("WinLoss"), null_if_empty(r.get("CloseDate")), r.get("KnowledgeStatus"))
            for r in data["opportunities"]
        ],
        "Proposals": [
            (r.get("ProposalID"), r.get("ProjectID"), r.get("ProposalType"), r.get("ProposalTheme"), r.get("KeyMessage"), r.get("Differentiator"), r.get("Result"), r.get("KnowledgeStatus"))
            for r in data["proposals"]
        ],
        "ProjectFinancials": [
            (r.get("ProjectID"), decimal_or_none(r.get("RevenueJPYMillion")), decimal_or_none(r.get("CostJPYMillion")), decimal_or_none(r.get("ProfitJPYMillion")), decimal_or_none(r.get("ProfitMarginPct")), decimal_or_none(r.get("EffortPersonMonths")), decimal_or_none(r.get("EffortReductionPct")), r.get("FinancialStatus"), r.get("KnowledgeStatus"))
            for r in data["financials"]
        ],
        "Requirements": [
            (r.get("RequirementID"), r.get("ProjectID"), r.get("Category"), r.get("RequirementName"), r.get("Description"), r.get("Priority"), r.get("KnowledgeStatus"))
            for r in data["requirements"]
        ],
        "Features": [
            (r.get("FeatureID"), r.get("ProjectID"), r.get("FeatureName"), r.get("Category"), r.get("Description"), r.get("DeliveryStatus"), r.get("KnowledgeStatus"))
            for r in data["features"]
        ],
        "Risks": [
            (r.get("RiskID"), r.get("ProjectID"), r.get("Category"), r.get("RiskName"), r.get("Description"), r.get("Severity"), r.get("Status"), r.get("Mitigation"), r.get("KnowledgeStatus"))
            for r in data["risks"]
        ],
        "BusinessOutcomes": [
            (r.get("OutcomeID"), r.get("ProjectID"), r.get("OutcomeType"), r.get("MetricName"), decimal_or_none(r.get("BeforeValue")), decimal_or_none(r.get("AfterValue")), r.get("Unit"), decimal_or_none(r.get("ImprovementPct")), r.get("OutcomeStatus"), r.get("Description"), r.get("KnowledgeStatus"))
            for r in data["outcomes"]
        ],
        "Documents": [
            (r.get("sourceId"), r.get("projectId"), r.get("documentType"), r.get("title"), r.get("path"), r.get("knowledgeStatus"), "project-knowledge-index")
            for r in data["documents"]
        ],
        "ServiceCandidates": [],
        "CandidateScores": [],
        "CandidateMetrics": [],
        "CandidateIceAxes": [],
        "CandidateIceFactors": [],
        "CandidateSupportingProjects": [],
        "CandidateReusableAssets": [],
        "CandidateStandardizationGaps": [],
        "CandidateRisks": [],
        "CandidateManagementDecisions": [],
        "CandidateDecisionItems": [],
    }

    for candidate in candidates:
        candidate_id = candidate["candidateId"]
        model = candidate.get("recommendedBusinessModel", {})
        rows["ServiceCandidates"].append((
            candidate_id,
            candidate.get("rank"),
            candidate.get("name"),
            candidate.get("executiveSummary"),
            candidate.get("businessReason"),
            model.get("current"),
            model.get("next"),
            model.get("futureOption"),
            model.get("rationale"),
            json.dumps(candidate, ensure_ascii=False),
        ))
        scores = candidate.get("scores", {})
        rows["CandidateScores"].append((candidate_id, scores.get("priority"), scores.get("profitability"), scores.get("reusability"), scores.get("standardization"), scores.get("recurringRevenue"), scores.get("saasReadiness"), scores.get("feasibility"), scores.get("confidence")))
        metrics = candidate.get("metrics", {})
        rows["CandidateMetrics"].append((candidate_id, metrics.get("supportingProjectCount"), metrics.get("industryCount"), metrics.get("winRate"), metrics.get("averageMarginRate"), metrics.get("averageEffortReductionRate"), metrics.get("wonRevenue")))

        ice = candidate.get("ice") or {}
        for axis_name in ("impact", "confidence", "ease"):
            axis = ice.get(axis_name) or {}
            rows["CandidateIceAxes"].append((candidate_id, axis_name, axis.get("score"), axis.get("summary"), ice.get("calculationMethod"), ice.get("formulaVersion")))
            for order, factor in enumerate(axis.get("factors", []), start=1):
                rows["CandidateIceFactors"].append((candidate_id, axis_name, order, factor.get("name"), factor.get("value"), factor.get("contribution")))

        for project in candidate.get("supportingProjects", []):
            rows["CandidateSupportingProjects"].append((candidate_id, project.get("projectId"), project.get("projectName"), project.get("industry"), project.get("evidenceSummary"), join_ids(project.get("sourceIds"))))
        for asset in candidate.get("reusableAssets", []):
            rows["CandidateReusableAssets"].append((candidate_id, asset.get("name"), asset.get("type"), asset.get("occurrenceCount"), asset.get("totalProjectCount"), asset.get("readinessScore"), asset.get("currentState"), asset.get("nextAction"), join_ids(asset.get("sourceIds"))))
        for order, gap in enumerate(candidate.get("standardizationGaps", []), start=1):
            rows["CandidateStandardizationGaps"].append((candidate_id, order, gap.get("category"), gap.get("currentState"), gap.get("targetState"), gap.get("priority"), gap.get("effort"), gap.get("dependency"), join_ids(gap.get("sourceIds"))))
        for order, risk in enumerate(candidate.get("risks", []), start=1):
            rows["CandidateRisks"].append((candidate_id, order, risk.get("name"), risk.get("impact"), risk.get("likelihood"), risk.get("mitigation"), join_ids(risk.get("sourceIds"))))

        decision = candidate.get("managementDecision") or {}
        rows["CandidateManagementDecisions"].append((candidate_id, decision.get("decision"), decision.get("investmentLevel"), decision.get("timeHorizon"), join_ids(decision.get("sourceIds"))))
        for item_type, key in (("Next90Days", "next90Days"), ("SuccessCriteria", "successCriteria"), ("StopOrReviewCriteria", "stopOrReviewCriteria")):
            for order, item in enumerate(decision.get(key, []), start=1):
                rows["CandidateDecisionItems"].append((candidate_id, item_type, order, item.get("text"), join_ids(item.get("sourceIds"))))

    return rows


def ensure_schema(connection: pyodbc.Connection) -> None:
    cursor = connection.cursor()
    statements = [statement.strip() for statement in schema_sql().split("\nGO\n") if statement.strip()]
    for statement in statements:
        cursor.execute(statement)
    cursor.close()


def clear_tables(connection: pyodbc.Connection) -> None:
    cursor = connection.cursor()
    for table in DELETE_ORDER:
        cursor.execute(f"delete from dbo.{table}")
    cursor.close()


def insert_rows(connection: pyodbc.Connection, rows: dict[str, list[tuple[Any, ...]]], verbose: bool) -> None:
    insert_sql = {
        "Customers": "insert into dbo.Customers values (?, ?, ?, ?, ?, ?)",
        "Projects": "insert into dbo.Projects values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        "Opportunities": "insert into dbo.Opportunities values (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        "Proposals": "insert into dbo.Proposals values (?, ?, ?, ?, ?, ?, ?, ?)",
        "ProjectFinancials": "insert into dbo.ProjectFinancials values (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        "Requirements": "insert into dbo.Requirements values (?, ?, ?, ?, ?, ?, ?)",
        "Features": "insert into dbo.Features values (?, ?, ?, ?, ?, ?, ?)",
        "Risks": "insert into dbo.Risks values (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        "BusinessOutcomes": "insert into dbo.BusinessOutcomes values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        "Documents": "insert into dbo.Documents values (?, ?, ?, ?, ?, ?, ?)",
        "ServiceCandidates": "insert into dbo.ServiceCandidates values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        "CandidateScores": "insert into dbo.CandidateScores values (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        "CandidateMetrics": "insert into dbo.CandidateMetrics values (?, ?, ?, ?, ?, ?, ?)",
        "CandidateIceAxes": "insert into dbo.CandidateIceAxes values (?, ?, ?, ?, ?, ?)",
        "CandidateIceFactors": "insert into dbo.CandidateIceFactors values (?, ?, ?, ?, ?, ?)",
        "CandidateSupportingProjects": "insert into dbo.CandidateSupportingProjects values (?, ?, ?, ?, ?, ?)",
        "CandidateReusableAssets": "insert into dbo.CandidateReusableAssets values (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        "CandidateStandardizationGaps": "insert into dbo.CandidateStandardizationGaps values (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        "CandidateRisks": "insert into dbo.CandidateRisks values (?, ?, ?, ?, ?, ?, ?)",
        "CandidateManagementDecisions": "insert into dbo.CandidateManagementDecisions values (?, ?, ?, ?, ?)",
        "CandidateDecisionItems": "insert into dbo.CandidateDecisionItems values (?, ?, ?, ?, ?)",
    }
    order = [table for table in reversed(DELETE_ORDER) if table in insert_sql]
    cursor = connection.cursor()
    cursor.fast_executemany = True
    for table in order:
        table_rows = rows.get(table, [])
        if not table_rows:
            continue
        if verbose:
            print(f"Inserting {table}: {len(table_rows)}")
        cursor.executemany(insert_sql[table], table_rows)
    cursor.close()


def print_counts(rows: dict[str, list[tuple[Any, ...]]]) -> None:
    for table in sorted(rows):
        print(f"{table}: {len(rows[table])}")


def null_if_empty(value: Any) -> Any:
    return None if value in (None, "") else value


def decimal_or_none(value: Any) -> Any:
    if value in (None, ""):
        return None
    return value


def join_ids(values: Iterable[str] | None) -> str | None:
    if not values:
        return None
    return ",".join(str(value) for value in values)


def schema_sql() -> str:
    return r'''
IF OBJECT_ID('dbo.vCandidate90DayDecisions', 'V') IS NOT NULL DROP VIEW dbo.vCandidate90DayDecisions
GO
IF OBJECT_ID('dbo.vCandidateSaasGaps', 'V') IS NOT NULL DROP VIEW dbo.vCandidateSaasGaps
GO
IF OBJECT_ID('dbo.vCandidateEvidenceProjects', 'V') IS NOT NULL DROP VIEW dbo.vCandidateEvidenceProjects
GO
IF OBJECT_ID('dbo.vCandidateIceBreakdown', 'V') IS NOT NULL DROP VIEW dbo.vCandidateIceBreakdown
GO
IF OBJECT_ID('dbo.vTopCandidates', 'V') IS NOT NULL DROP VIEW dbo.vTopCandidates
GO
IF OBJECT_ID('dbo.CandidateDecisionItems', 'U') IS NULL CREATE TABLE dbo.CandidateDecisionItems (CandidateID nvarchar(64) not null, ItemType nvarchar(50) not null, ItemOrder int not null, ItemText nvarchar(max) null, SourceIDs nvarchar(max) null, constraint PK_CandidateDecisionItems primary key (CandidateID, ItemType, ItemOrder))
GO
IF OBJECT_ID('dbo.CandidateManagementDecisions', 'U') IS NULL CREATE TABLE dbo.CandidateManagementDecisions (CandidateID nvarchar(64) not null primary key, Decision nvarchar(max) null, InvestmentLevel nvarchar(100) null, TimeHorizon nvarchar(100) null, SourceIDs nvarchar(max) null)
GO
IF OBJECT_ID('dbo.CandidateRisks', 'U') IS NULL CREATE TABLE dbo.CandidateRisks (CandidateID nvarchar(64) not null, RiskOrder int not null, RiskName nvarchar(200) null, Impact nvarchar(50) null, Likelihood nvarchar(50) null, Mitigation nvarchar(max) null, SourceIDs nvarchar(max) null, constraint PK_CandidateRisks primary key (CandidateID, RiskOrder))
GO
IF OBJECT_ID('dbo.CandidateStandardizationGaps', 'U') IS NULL CREATE TABLE dbo.CandidateStandardizationGaps (CandidateID nvarchar(64) not null, GapOrder int not null, Category nvarchar(100) null, CurrentState nvarchar(max) null, TargetState nvarchar(max) null, Priority nvarchar(50) null, Effort nvarchar(50) null, Dependency nvarchar(max) null, SourceIDs nvarchar(max) null, constraint PK_CandidateStandardizationGaps primary key (CandidateID, GapOrder))
GO
IF OBJECT_ID('dbo.CandidateReusableAssets', 'U') IS NULL CREATE TABLE dbo.CandidateReusableAssets (CandidateID nvarchar(64) not null, AssetName nvarchar(200) not null, AssetType nvarchar(100) null, OccurrenceCount int null, TotalProjectCount int null, ReadinessScore int null, CurrentState nvarchar(max) null, NextAction nvarchar(max) null, SourceIDs nvarchar(max) null, constraint PK_CandidateReusableAssets primary key (CandidateID, AssetName))
GO
IF OBJECT_ID('dbo.CandidateSupportingProjects', 'U') IS NULL CREATE TABLE dbo.CandidateSupportingProjects (CandidateID nvarchar(64) not null, ProjectID nvarchar(32) not null, ProjectName nvarchar(300) null, Industry nvarchar(100) null, EvidenceSummary nvarchar(max) null, SourceIDs nvarchar(max) null, constraint PK_CandidateSupportingProjects primary key (CandidateID, ProjectID))
GO
IF OBJECT_ID('dbo.CandidateIceFactors', 'U') IS NULL CREATE TABLE dbo.CandidateIceFactors (CandidateID nvarchar(64) not null, AxisName nvarchar(32) not null, FactorOrder int not null, FactorName nvarchar(200) null, FactorValue nvarchar(100) null, Contribution decimal(9,2) null, constraint PK_CandidateIceFactors primary key (CandidateID, AxisName, FactorOrder))
GO
IF OBJECT_ID('dbo.CandidateIceAxes', 'U') IS NULL CREATE TABLE dbo.CandidateIceAxes (CandidateID nvarchar(64) not null, AxisName nvarchar(32) not null, Score int null, Summary nvarchar(max) null, CalculationMethod nvarchar(100) null, FormulaVersion nvarchar(100) null, constraint PK_CandidateIceAxes primary key (CandidateID, AxisName))
GO
IF OBJECT_ID('dbo.CandidateMetrics', 'U') IS NULL CREATE TABLE dbo.CandidateMetrics (CandidateID nvarchar(64) not null primary key, SupportingProjectCount int null, IndustryCount int null, WinRate decimal(9,2) null, AverageMarginRate decimal(9,2) null, AverageEffortReductionRate decimal(9,2) null, WonRevenue decimal(18,2) null)
GO
IF OBJECT_ID('dbo.CandidateScores', 'U') IS NULL CREATE TABLE dbo.CandidateScores (CandidateID nvarchar(64) not null primary key, PriorityScore int null, Profitability int null, Reusability int null, Standardization int null, RecurringRevenue int null, SaasReadiness int null, Feasibility int null, Confidence int null)
GO
IF OBJECT_ID('dbo.ServiceCandidates', 'U') IS NULL CREATE TABLE dbo.ServiceCandidates (CandidateID nvarchar(64) not null primary key, Rank int not null, Name nvarchar(300) not null, ExecutiveSummary nvarchar(max) null, BusinessReason nvarchar(max) null, CurrentBusinessModel nvarchar(100) null, NextBusinessModel nvarchar(100) null, FutureBusinessModel nvarchar(100) null, BusinessModelRationale nvarchar(max) null, RawJson nvarchar(max) null)
GO
IF OBJECT_ID('dbo.Documents', 'U') IS NULL CREATE TABLE dbo.Documents (SourceID nvarchar(100) not null primary key, ProjectID nvarchar(32) null, DocumentType nvarchar(100) null, Title nvarchar(300) null, SourcePath nvarchar(500) null, KnowledgeStatus nvarchar(50) null, SearchIndexName nvarchar(100) not null default 'project-knowledge-index')
GO
IF OBJECT_ID('dbo.BusinessOutcomes', 'U') IS NULL CREATE TABLE dbo.BusinessOutcomes (OutcomeID nvarchar(64) not null primary key, ProjectID nvarchar(32) null, OutcomeType nvarchar(100) null, MetricName nvarchar(200) null, BeforeValue decimal(18,2) null, AfterValue decimal(18,2) null, Unit nvarchar(50) null, ImprovementPct decimal(9,2) null, OutcomeStatus nvarchar(100) null, Description nvarchar(max) null, KnowledgeStatus nvarchar(50) null)
GO
IF OBJECT_ID('dbo.Risks', 'U') IS NULL CREATE TABLE dbo.Risks (RiskID nvarchar(64) not null primary key, ProjectID nvarchar(32) null, Category nvarchar(100) null, RiskName nvarchar(300) null, Description nvarchar(max) null, Severity nvarchar(50) null, Status nvarchar(100) null, Mitigation nvarchar(max) null, KnowledgeStatus nvarchar(50) null)
GO
IF OBJECT_ID('dbo.Features', 'U') IS NULL CREATE TABLE dbo.Features (FeatureID nvarchar(64) not null primary key, ProjectID nvarchar(32) null, FeatureName nvarchar(300) null, Category nvarchar(100) null, Description nvarchar(max) null, DeliveryStatus nvarchar(100) null, KnowledgeStatus nvarchar(50) null)
GO
IF OBJECT_ID('dbo.Requirements', 'U') IS NULL CREATE TABLE dbo.Requirements (RequirementID nvarchar(64) not null primary key, ProjectID nvarchar(32) null, Category nvarchar(100) null, RequirementName nvarchar(300) null, Description nvarchar(max) null, Priority nvarchar(50) null, KnowledgeStatus nvarchar(50) null)
GO
IF OBJECT_ID('dbo.ProjectFinancials', 'U') IS NULL CREATE TABLE dbo.ProjectFinancials (ProjectID nvarchar(32) not null primary key, RevenueJPYMillion decimal(18,2) null, CostJPYMillion decimal(18,2) null, ProfitJPYMillion decimal(18,2) null, ProfitMarginPct decimal(9,2) null, EffortPersonMonths decimal(9,2) null, EffortReductionPct decimal(9,2) null, FinancialStatus nvarchar(50) null, KnowledgeStatus nvarchar(50) null)
GO
IF OBJECT_ID('dbo.Proposals', 'U') IS NULL CREATE TABLE dbo.Proposals (ProposalID nvarchar(64) not null primary key, ProjectID nvarchar(32) null, ProposalType nvarchar(200) null, ProposalTheme nvarchar(200) null, KeyMessage nvarchar(max) null, Differentiator nvarchar(max) null, Result nvarchar(50) null, KnowledgeStatus nvarchar(50) null)
GO
IF OBJECT_ID('dbo.Opportunities', 'U') IS NULL CREATE TABLE dbo.Opportunities (OpportunityID nvarchar(64) not null primary key, CustomerID nvarchar(32) null, ProjectID nvarchar(32) null, OpportunityName nvarchar(300) null, Stage nvarchar(100) null, AmountJPYMillion decimal(18,2) null, WinLoss nvarchar(50) null, CloseDate date null, KnowledgeStatus nvarchar(50) null)
GO
IF OBJECT_ID('dbo.Projects', 'U') IS NULL CREATE TABLE dbo.Projects (ProjectID nvarchar(32) not null primary key, CustomerID nvarchar(32) null, ProjectName nvarchar(300) not null, Industry nvarchar(100) null, ProjectTheme nvarchar(200) null, StartDate date null, EndDate date null, Status nvarchar(100) null, WinLoss nvarchar(50) null, KnowledgeStatus nvarchar(50) null)
GO
IF OBJECT_ID('dbo.Customers', 'U') IS NULL CREATE TABLE dbo.Customers (CustomerID nvarchar(32) not null primary key, CustomerName nvarchar(200) not null, Industry nvarchar(100) null, Region nvarchar(100) null, Segment nvarchar(100) null, KnowledgeStatus nvarchar(50) null)
GO
CREATE OR ALTER VIEW dbo.vTopCandidates AS SELECT c.Rank, c.CandidateID, c.Name, s.PriorityScore AS IceScore, m.WinRate, m.AverageMarginRate, m.WonRevenue, m.SupportingProjectCount, m.IndustryCount, s.SaasReadiness, c.CurrentBusinessModel, c.NextBusinessModel, c.FutureBusinessModel FROM dbo.ServiceCandidates c LEFT JOIN dbo.CandidateScores s ON c.CandidateID = s.CandidateID LEFT JOIN dbo.CandidateMetrics m ON c.CandidateID = m.CandidateID
GO
CREATE OR ALTER VIEW dbo.vCandidateIceBreakdown AS SELECT c.Rank, c.CandidateID, c.Name AS CandidateName, s.PriorityScore AS IceScore, a.AxisName, a.Score AS AxisScore, a.Summary, f.FactorOrder, f.FactorName, f.FactorValue, f.Contribution FROM dbo.ServiceCandidates c JOIN dbo.CandidateScores s ON c.CandidateID = s.CandidateID JOIN dbo.CandidateIceAxes a ON c.CandidateID = a.CandidateID LEFT JOIN dbo.CandidateIceFactors f ON a.CandidateID = f.CandidateID AND a.AxisName = f.AxisName
GO
CREATE OR ALTER VIEW dbo.vCandidateEvidenceProjects AS SELECT c.Rank, c.CandidateID, c.Name AS CandidateName, p.ProjectID, p.ProjectName, p.Industry, p.EvidenceSummary, p.SourceIDs FROM dbo.ServiceCandidates c JOIN dbo.CandidateSupportingProjects p ON c.CandidateID = p.CandidateID
GO
CREATE OR ALTER VIEW dbo.vCandidateSaasGaps AS SELECT c.Rank, c.CandidateID, c.Name AS CandidateName, g.GapOrder, g.Category, g.CurrentState, g.TargetState, g.Priority, g.Effort, g.Dependency, g.SourceIDs FROM dbo.ServiceCandidates c JOIN dbo.CandidateStandardizationGaps g ON c.CandidateID = g.CandidateID
GO
CREATE OR ALTER VIEW dbo.vCandidate90DayDecisions AS SELECT c.Rank, c.CandidateID, c.Name AS CandidateName, d.Decision, d.InvestmentLevel, d.TimeHorizon, i.ItemType, i.ItemOrder, i.ItemText, i.SourceIDs FROM dbo.ServiceCandidates c LEFT JOIN dbo.CandidateManagementDecisions d ON c.CandidateID = d.CandidateID LEFT JOIN dbo.CandidateDecisionItems i ON c.CandidateID = i.CandidateID
'''


if __name__ == "__main__":
    main()
