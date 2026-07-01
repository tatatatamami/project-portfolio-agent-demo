from __future__ import annotations

from collections import Counter, defaultdict
from statistics import mean
from typing import Any

from models import LoadedData


CANDIDATE_NAME_BY_THEME = {
    "AI-ready Data Foundation": "AIデータ活用基盤オファリング",
    "API Modernization": "APIモダナイゼーション・アクセラレータ",
    "AI Agent Production": "AIエージェント本番化・運用プラットフォーム",
}

BUSINESS_MODEL_BY_THEME = {
    "AI-ready Data Foundation": ("Standard Offering", "Managed Service", "SaaS", "データ基盤標準テンプレートを先行商品化し、運用監視を継続収益化する余地が大きい。"),
    "API Modernization": ("Standard Offering", "Managed Service", "SaaS", "移行診断、API標準部品、運用支援を段階的に標準化できる。"),
    "AI Agent Production": ("Managed Service", "Standard Offering", "SaaS", "評価、監視、安全対策を運用サービスとして束ねると再利用しやすい。"),
}


def build_metrics(data: LoadedData, candidate_limit: int | None = None) -> dict[str, Any]:
    projects = _approved(data.projects)
    financials_by_project = {row["ProjectID"]: row for row in _approved(data.financials)}
    docs_by_project = _group_documents(data.documents)
    requirements_by_theme = _approved_names_by_theme(data.requirements, projects, "RequirementName")
    features_by_theme = _approved_names_by_theme(data.features, projects, "FeatureName")
    risks_by_theme = _approved_names_by_theme(data.risks, projects, "RiskName")

    summaries = []
    for theme, theme_projects in sorted(_group_by(projects, "ProjectTheme").items()):
        won_projects = [p for p in theme_projects if p["WinLoss"] == "Won"]
        lost_projects = [p for p in theme_projects if p["WinLoss"] == "Lost"]
        won_financials = [financials_by_project[p["ProjectID"]] for p in won_projects]
        lost_financials = [financials_by_project[p["ProjectID"]] for p in lost_projects]
        total_won_revenue_m = sum(_number(row["RevenueJPYMillion"]) for row in won_financials)
        total_won_profit_m = sum(_number(row["ProfitJPYMillion"]) for row in won_financials)
        lost_bid_cost_m = sum(_number(row["CostJPYMillion"]) for row in lost_financials)
        average_margin = round(mean(_number(row["ProfitMarginPct"]) for row in won_financials), 1) if won_financials else 0.0
        average_effort = round(mean(_number(row["EffortReductionPct"]) for row in won_financials), 1) if won_financials else 0.0
        win_rate = round(len(won_projects) / len(theme_projects) * 100, 1) if theme_projects else 0.0
        industry_count = len({p["Industry"] for p in theme_projects})
        project_ids = [p["ProjectID"] for p in theme_projects]
        source_ids = [doc["sourceId"] for project_id in project_ids for doc in docs_by_project.get(project_id, [])]
        common_requirements = _top_counter_items(requirements_by_theme[theme], 8)
        common_features = _top_counter_items(features_by_theme[theme], 8)

        scores = _score_candidate(
            average_margin=average_margin,
            total_won_revenue_m=total_won_revenue_m,
            common_feature_count=len(common_features),
            common_requirement_count=len(common_requirements),
            industry_count=industry_count,
            supporting_count=len(theme_projects),
            document_count=len(source_ids),
            lost_count=len(lost_projects),
            average_effort=average_effort,
        )
        summaries.append({
            "theme": theme,
            "candidateId": "",
            "rank": 0,
            "name": CANDIDATE_NAME_BY_THEME.get(theme, f"{theme} オファリング"),
            "metrics": {
                "supportingProjectCount": len(theme_projects),
                "industryCount": industry_count,
                "winRate": win_rate,
                "averageMarginRate": average_margin,
                "averageEffortReductionRate": average_effort,
                "wonRevenue": int(total_won_revenue_m * 1_000_000),
                "totalWonRevenueJPYMillion": int(total_won_revenue_m),
                "totalWonProfitJPYMillion": int(total_won_profit_m),
                "lostBidCostJPYMillion": int(lost_bid_cost_m),
            },
            "scores": scores,
            "commonRequirements": common_requirements,
            "commonFeatures": common_features,
            "commonRisks": _top_counter_items(risks_by_theme[theme], 6),
            "supportingProjects": [_supporting_project(project, docs_by_project.get(project["ProjectID"], [])) for project in theme_projects],
            "sourceIds": source_ids,
        })

    summaries.sort(key=lambda item: (-item["scores"]["priority"], item["theme"]))
    if candidate_limit:
        summaries = summaries[:candidate_limit]
    for index, summary in enumerate(summaries, start=1):
        summary["rank"] = index
        summary["candidateId"] = f"CAND-{index:03d}"

    won_financials_all = [financials_by_project[p["ProjectID"]] for p in projects if p["WinLoss"] == "Won"]
    return {
        "source": {
            "projectCount": len(projects),
            "wonCount": sum(1 for p in projects if p["WinLoss"] == "Won"),
            "lostCount": sum(1 for p in projects if p["WinLoss"] == "Lost"),
            "documentCount": len(data.documents),
        },
        "dashboardSummary": {
            "projectCount": len(projects),
            "candidateCount": len(summaries),
            "wonRevenue": int(sum(_number(row["RevenueJPYMillion"]) for row in won_financials_all) * 1_000_000),
            "averageMarginRate": round(mean(_number(row["ProfitMarginPct"]) for row in won_financials_all), 1),
        },
        "candidates": summaries,
    }


def build_dashboard_candidate(summary: dict[str, Any], llm_payload: dict[str, Any] | None = None) -> dict[str, Any]:
    generated = llm_payload or _fallback_generated_content(summary)
    return {
        "candidateId": summary["candidateId"],
        "rank": summary["rank"],
        "name": generated.get("name") or summary["name"],
        "executiveSummary": generated["executiveSummary"],
        "businessReason": generated["businessReason"],
        "scores": summary["scores"],
        "metrics": {key: value for key, value in summary["metrics"].items() if not key.endswith("JPYMillion")},
        "recommendedBusinessModel": generated["recommendedBusinessModel"],
        "supportingProjects": summary["supportingProjects"],
        "reusableAssets": generated["reusableAssets"],
        "standardizationGaps": generated["standardizationGaps"],
        "successFactors": generated["successFactors"],
        "failureFactors": generated["failureFactors"],
        "risks": generated["risks"],
        "managementDecision": generated["managementDecision"],
    }


def _approved(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [row for row in rows if row.get("KnowledgeStatus") == "Approved"]


def _group_by(rows: list[dict[str, str]], key: str) -> dict[str, list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[row[key]].append(row)
    return grouped


def _group_documents(documents: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for doc in documents:
        project_id = doc["metadata"].get("projectId")
        if project_id and project_id != "GLOBAL":
            grouped[project_id].append(doc)
    return grouped


def _approved_names_by_theme(rows: list[dict[str, str]], projects: list[dict[str, str]], name_key: str) -> dict[str, Counter[str]]:
    theme_by_project = {project["ProjectID"]: project["ProjectTheme"] for project in projects}
    counters: dict[str, Counter[str]] = defaultdict(Counter)
    for row in _approved(rows):
        theme = theme_by_project.get(row["ProjectID"])
        if theme:
            counters[theme][row[name_key]] += 1
    return counters


def _top_counter_items(counter: Counter[str], limit: int) -> list[dict[str, Any]]:
    return [{"name": name, "occurrenceCount": count} for name, count in counter.most_common(limit)]


def _supporting_project(project: dict[str, str], documents: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "projectId": project["ProjectID"],
        "projectName": project["ProjectName"],
        "industry": project["Industry"],
        "evidenceSummary": f"{project['ProjectTheme']} に関する {project['WinLoss']} 案件。{len(documents)} 件の案件文書を根拠として利用。",
        "sourceIds": [doc["sourceId"] for doc in documents],
    }


def _score_candidate(**values: float | int) -> dict[str, int]:
    profitability = _clamp(values["average_margin"] * 2.0 + values["total_won_revenue_m"] / 45)
    reusability = _clamp(values["common_feature_count"] * 8 + values["industry_count"] * 10 + values["supporting_count"] * 4)
    standardization = _clamp(values["common_requirement_count"] * 9 + values["common_feature_count"] * 4)
    recurring = _clamp(45 + values["average_effort"] + values["common_feature_count"] * 3)
    saas = _clamp(35 + values["common_requirement_count"] * 4 + values["common_feature_count"] * 3 - values["lost_count"] * 6)
    feasibility = _clamp(85 - values["lost_count"] * 8 + values["average_effort"] / 2)
    confidence = _clamp(values["supporting_count"] * 12 + values["document_count"] * 4 + values["industry_count"] * 6)
    priority = _clamp(
        profitability * 0.24
        + reusability * 0.18
        + standardization * 0.16
        + recurring * 0.12
        + saas * 0.10
        + feasibility * 0.10
        + confidence * 0.10
    )
    return {
        "priority": priority,
        "profitability": profitability,
        "reusability": reusability,
        "standardization": standardization,
        "recurringRevenue": recurring,
        "saasReadiness": saas,
        "feasibility": feasibility,
        "confidence": confidence,
    }


def _fallback_generated_content(summary: dict[str, Any]) -> dict[str, Any]:
    theme = summary["theme"]
    current, next_model, future, rationale = BUSINESS_MODEL_BY_THEME.get(theme, ("Standard Offering", "Managed Service", "SaaS", "共通要件と再利用部品を段階的に標準化できる。"))
    asset_sources = summary["sourceIds"][:3]
    return {
        "name": summary["name"],
        "executiveSummary": f"{summary['metrics']['supportingProjectCount']} 件の案件実績から、{summary['name']} は事業化候補として優先検討できる。",
        "businessReason": f"受注率 {summary['metrics']['winRate']}%、平均利益率 {summary['metrics']['averageMarginRate']}%、共通要件 {len(summary['commonRequirements'])} 種を確認。数値はPython集計値を使用。",
        "recommendedBusinessModel": {"current": current, "next": next_model, "futureOption": future, "rationale": rationale},
        "reusableAssets": [
            {
                "name": item["name"],
                "type": "Feature" if index < len(summary["commonFeatures"]) else "Requirement",
                "occurrenceCount": item["occurrenceCount"],
                "totalProjectCount": summary["metrics"]["supportingProjectCount"],
                "readinessScore": _clamp(item["occurrenceCount"] / summary["metrics"]["supportingProjectCount"] * 100),
                "currentState": "複数案件で利用実績あり",
                "nextAction": "標準テンプレート、設計ガイド、見積り前提へ整理する",
                "sourceIds": asset_sources,
            }
            for index, item in enumerate((summary["commonFeatures"] + summary["commonRequirements"])[:5])
        ],
        "standardizationGaps": [
            {"category": "Delivery", "currentState": "案件別に成果物粒度が異なる", "targetState": "標準スコープ、導入手順、完了条件を定義", "effort": "Medium", "priority": "High", "dependency": "営業・Delivery双方のレビュー"},
            {"category": "Operations", "currentState": "運用項目が案件ごとに分散", "targetState": "監視、評価、改善サイクルを標準メニュー化", "effort": "Medium", "priority": "Medium", "dependency": "運用責任範囲の明確化"},
        ],
        "successFactors": ["共通要件を標準スコープに固定する", "根拠文書を再利用可能な資産に整理する", "案件固有対応の上限を定義する"],
        "failureFactors": ["案件固有要件を標準機能に混在させる", "所有者と更新責任を決めない", "運用フェーズの収益化を後回しにする"],
        "risks": [
            {"name": item["name"], "impact": "Medium", "likelihood": "Medium", "mitigation": "標準化前に責任範囲、適用条件、除外条件を明記する", "sourceIds": asset_sources}
            for item in summary["commonRisks"][:3]
        ],
        "managementDecision": {
            "decision": "標準化検討を開始し、90日以内に提供範囲と投資判断を確定する",
            "investmentLevel": "Medium",
            "timeHorizon": "90 days",
            "next90Days": ["再利用資産の棚卸しを完了する", "標準スコープと除外条件を定義する", "パイロット顧客候補を選定する"],
            "successCriteria": ["標準提案テンプレートが完成", "再利用資産の所有者が決定", "次案件で再利用可能な見積り前提が承認"],
            "stopOrReviewCriteria": ["標準化対象が2案件未満", "案件固有対応が主要工数を占める", "運用責任範囲が合意できない"],
        },
    }


def _number(value: str | int | float | None) -> float:
    if value in (None, "", "null"):
        return 0.0
    return float(value)


def _clamp(value: float) -> int:
    return max(0, min(100, int(round(value))))
