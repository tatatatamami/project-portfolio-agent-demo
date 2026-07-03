from __future__ import annotations

import argparse
import copy
import json
import re
from collections import Counter, defaultdict
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from data_loader import load_portfolio_data
from metrics import build_dashboard_candidate, build_metrics
from models import LoadedData


def main() -> int:
    parser = argparse.ArgumentParser(description="Discover service candidate themes from project evidence without using ProjectTheme.")
    parser.add_argument("--input-dir", default="test-data")
    parser.add_argument("--output-dir", default="analysis/output")
    parser.add_argument("--candidate-limit", type=int, default=None)
    parser.add_argument("--similarity-threshold", type=float, default=0.35)
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    data = load_portfolio_data(input_dir)
    discovery = discover_project_themes(data, args.similarity_threshold)
    discovered_data = apply_discovered_themes(data, discovery["projectThemeById"])
    calculated = build_metrics(discovered_data, args.candidate_limit)
    dashboard_candidates = [build_dashboard_candidate(candidate_summary) for candidate_summary in calculated["candidates"]]
    generated_at = datetime.now(UTC).isoformat()

    dashboard_data = {
        "analysisRun": {
            "runId": str(uuid4()),
            "status": "completed",
            "generatedAt": generated_at,
            "sourceProjectCount": calculated["source"]["projectCount"],
            "modelProvider": "theme-discovery-dry-run",
            "modelDeployment": "none",
            "promptVersion": "v1-unknown-theme-discovery",
        },
        "dashboardSummary": calculated["dashboardSummary"],
        "themeDiscovery": discovery,
        "candidates": dashboard_candidates,
    }

    report = {
        "status": "completed",
        "generatedAt": generated_at,
        "inputProjectThemeUsed": False,
        "similarityThreshold": args.similarity_threshold,
        "clusterCount": len(discovery["clusters"]),
        "clusters": discovery["clusters"],
        "outputFiles": {
            "dashboardData": "analysis/output/dashboard-data-discovered-themes.json",
            "report": "analysis/output/theme-discovery-report.json",
        },
    }

    write_json(output_dir / "dashboard-data-discovered-themes.json", dashboard_data)
    write_json(output_dir / "theme-discovery-report.json", report)
    print(f"Generated {output_dir / 'dashboard-data-discovered-themes.json'}")
    print(f"Generated {output_dir / 'theme-discovery-report.json'}")
    print("Existing analysis/output/dashboard-data.json was not modified.")
    return 0


def discover_project_themes(data: LoadedData, similarity_threshold: float) -> dict[str, Any]:
    projects = [project for project in data.projects if project.get("KnowledgeStatus") == "Approved"]
    evidence_by_project = build_project_evidence(data)
    graph: dict[str, set[str]] = {project["ProjectID"]: set() for project in projects}
    similarities = []

    for left_index, left in enumerate(projects):
        for right in projects[left_index + 1:]:
            left_id = left["ProjectID"]
            right_id = right["ProjectID"]
            similarity = jaccard(evidence_by_project[left_id], evidence_by_project[right_id])
            if similarity >= similarity_threshold:
                graph[left_id].add(right_id)
                graph[right_id].add(left_id)
                similarities.append({"leftProjectId": left_id, "rightProjectId": right_id, "similarity": round(similarity, 3)})

    project_by_id = {project["ProjectID"]: project for project in projects}
    clusters = []
    project_theme_by_id = {}
    visited = set()
    for project in projects:
        project_id = project["ProjectID"]
        if project_id in visited:
            continue
        component = connected_component(project_id, graph, visited)
        cluster_projects = [project_by_id[item] for item in sorted(component)]
        theme_name = infer_theme_name(cluster_projects, data)
        for item in component:
            project_theme_by_id[item] = theme_name
        clusters.append({
            "theme": theme_name,
            "projectIds": [item["ProjectID"] for item in cluster_projects],
            "projectNames": [item["ProjectName"] for item in cluster_projects],
            "industries": sorted({item["Industry"] for item in cluster_projects}),
            "winLoss": dict(Counter(item["WinLoss"] for item in cluster_projects)),
            "topSignals": top_cluster_signals(cluster_projects, data),
        })

    clusters.sort(key=lambda item: (-len(item["projectIds"]), item["theme"]))
    return {
        "method": "jaccard-connected-components",
        "inputProjectThemeUsed": False,
        "evidenceFields": ["RequirementName", "FeatureName", "RiskName"],
        "similarityThreshold": similarity_threshold,
        "projectThemeById": project_theme_by_id,
        "clusters": clusters,
        "similarProjectPairs": similarities,
    }


def build_project_evidence(data: LoadedData) -> dict[str, set[str]]:
    evidence: dict[str, set[str]] = defaultdict(set)
    for rows, keys in [
        (data.requirements, ["RequirementName"]),
        (data.features, ["FeatureName"]),
        (data.risks, ["RiskName"]),
    ]:
        for row in rows:
            if row.get("KnowledgeStatus") != "Approved":
                continue
            project_id = row["ProjectID"]
            for key in keys:
                value = row.get(key, "")
                if value:
                    evidence[project_id].add(f"phrase:{normalize_phrase(value)}")
                    evidence[project_id].update(tokenize(value))
    return evidence


def apply_discovered_themes(data: LoadedData, project_theme_by_id: dict[str, str]) -> LoadedData:
    projects = []
    for project in data.projects:
        updated = copy.deepcopy(project)
        updated["ProjectTheme"] = project_theme_by_id.get(project["ProjectID"], f"Discovered Theme - {project['ProjectID']}")
        projects.append(updated)
    return replace(data, projects=projects)


def connected_component(start: str, graph: dict[str, set[str]], visited: set[str]) -> set[str]:
    stack = [start]
    component = set()
    while stack:
        item = stack.pop()
        if item in visited:
            continue
        visited.add(item)
        component.add(item)
        stack.extend(sorted(graph[item] - visited))
    return component


def infer_theme_name(projects: list[dict[str, str]], data: LoadedData) -> str:
    signals = top_cluster_signals(projects, data)
    signal_names = [item["name"] for item in signals]
    joined = " ".join(signal_names).lower()
    if {"api gateway", "oauth / entra id", "api version management"}.intersection(name.lower() for name in signal_names):
        return "Discovered API Platform Modernization"
    if {"lakehouse", "data pipelines", "semantic model"}.intersection(name.lower() for name in signal_names):
        return "Discovered Data Foundation Platform"
    if {"grounded retrieval", "source display", "evaluation pipeline"}.intersection(name.lower() for name in signal_names):
        return "Discovered Grounded AI Agent Operations"
    if "api" in joined:
        return "Discovered API Service Theme"
    if "data" in joined or "lakehouse" in joined:
        return "Discovered Data Service Theme"
    if "agent" in joined or "retrieval" in joined:
        return "Discovered AI Agent Service Theme"
    return f"Discovered Theme: {', '.join(signal_names[:2])}"


def top_cluster_signals(projects: list[dict[str, str]], data: LoadedData) -> list[dict[str, Any]]:
    project_ids = {project["ProjectID"] for project in projects}
    counter: Counter[str] = Counter()
    for rows, key in [(data.features, "FeatureName"), (data.requirements, "RequirementName"), (data.risks, "RiskName")]:
        for row in rows:
            if row.get("KnowledgeStatus") == "Approved" and row.get("ProjectID") in project_ids:
                counter[row[key]] += 1
    return [{"name": name, "occurrenceCount": count} for name, count in counter.most_common(8)]


def tokenize(value: str) -> set[str]:
    return {token for token in re.findall(r"[a-z0-9]+", value.lower()) if len(token) >= 3}


def normalize_phrase(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lower())


def jaccard(left: set[str], right: set[str]) -> float:
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)


def write_json(path: Path, value: dict[str, Any] | list[Any]) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())