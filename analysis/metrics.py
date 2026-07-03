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

CANDIDATE_ID_BY_THEME = {
    "AI-ready Data Foundation": "CAND-001",
    "API Modernization": "CAND-002",
    "AI Agent Production": "CAND-003",
}

BUSINESS_MODEL_BY_THEME = {
    "AI-ready Data Foundation": ("Standard Offering", "Managed Service", "SaaS", "データ基盤標準テンプレートを先行商品化し、運用監視を継続収益化する余地が大きい。"),
    "API Modernization": ("Standard Offering", "Managed Service", "SaaS", "移行診断、API標準部品、運用支援を段階的に標準化できる。"),
    "AI Agent Production": ("Managed Service", "Standard Offering", "SaaS", "評価、監視、安全対策を運用サービスとして束ねると再利用しやすい。"),
}

IMPACT_WEIGHTS = {
    "winRate": 0.20,
    "averageMarginRate": 0.25,
    "wonRevenue": 0.20,
    "averageEffortReductionRate": 0.20,
    "industryBreadth": 0.15,
}

CONFIDENCE_WEIGHTS = {
    "evidenceVolume": 0.20,
    "industryDiversity": 0.15,
    "evidenceDocumentCoverage": 0.15,
    "commonPatternConsistency": 0.15,
    "outcomeConsistency": 0.20,
    "dataCompleteness": 0.15,
}

EASE_WEIGHTS = {
    "reusableAssetReadiness": 0.30,
    "standardizationReadiness": 0.25,
    "inverseGapBurden": 0.20,
    "inverseRiskBurden": 0.15,
    "inverseInvestmentBurden": 0.10,
}

BURDEN_LEVEL_SCORE = {
    "Low": 90,
    "Medium": 60,
    "High": 30,
}


def build_metrics(data: LoadedData, candidate_limit: int | None = None) -> dict[str, Any]:
    projects = _approved(data.projects)
    financials_by_project = {row["ProjectID"]: row for row in _approved(data.financials)}
    docs_by_project = _group_documents(data.documents)
    requirements_by_theme = _approved_names_by_theme(data.requirements, projects, "RequirementName")
    features_by_theme = _approved_names_by_theme(data.features, projects, "FeatureName")
    risks_by_theme = _approved_names_by_theme(data.risks, projects, "RiskName")
    requirement_sources_by_theme = _approved_sources_by_theme(data.requirements, projects, "RequirementName", "RequirementID")
    feature_sources_by_theme = _approved_sources_by_theme(data.features, projects, "FeatureName", "FeatureID")
    risk_sources_by_theme = _approved_sources_by_theme(data.risks, projects, "RiskName", "RiskID")
    risks_rows_by_theme = _approved_rows_by_theme(data.risks, projects)
    financials_rows_by_theme = _approved_rows_by_theme(data.financials, projects)

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
        common_requirements = _top_counter_items(requirements_by_theme[theme], 8, requirement_sources_by_theme[theme])
        common_features = _top_counter_items(features_by_theme[theme], 8, feature_sources_by_theme[theme])
        document_count = len(source_ids)
        common_pattern_consistency = _common_pattern_consistency(common_requirements + common_features, len(theme_projects))

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
        ice_inputs = {
            "supportingProjectCount": len(theme_projects),
            "industryCount": industry_count,
            "evidenceDocumentCount": document_count,
            "expectedDocumentCount": len(theme_projects) * 3,
            "commonPatternConsistency": common_pattern_consistency,
            "dataCompleteness": _data_completeness(theme_projects, financials_rows_by_theme[theme], docs_by_project),
            "reusableAssetReadiness": common_pattern_consistency,
            "standardizationReadiness": round((common_pattern_consistency * 0.7) + (min(100, (len(common_requirements) + len(common_features)) * 6) * 0.3), 1),
            "gapBurden": _standardization_gap_burden(lost_count=len(lost_projects), common_pattern_consistency=common_pattern_consistency, industry_count=industry_count, supporting_count=len(theme_projects)),
            "riskBurden": sum(1 for risk in risks_rows_by_theme[theme] if risk.get("Severity") == "High"),
        }
        ice_inputs["investmentBurdenLevel"] = _investment_burden_level(ice_inputs["gapBurden"], ice_inputs["riskBurden"], len(lost_projects))
        summaries.append({
            "theme": theme,
            "candidateId": CANDIDATE_ID_BY_THEME.get(theme, ""),
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
            "commonRisks": _top_counter_items(risks_by_theme[theme], 6, risk_sources_by_theme[theme]),
            "supportingProjects": [_supporting_project(project, docs_by_project.get(project["ProjectID"], [])) for project in theme_projects],
            "sourceIds": source_ids,
            "iceInputs": ice_inputs,
        })

    _apply_ice_scores(summaries)
    summaries.sort(key=lambda item: (-item["ice"]["score"], -item["ice"]["impact"]["score"], -item["ice"]["confidence"]["score"], -item["ice"]["ease"]["score"], item["candidateId"]))
    if candidate_limit:
        summaries = summaries[:candidate_limit]
    for index, summary in enumerate(summaries, start=1):
        summary["rank"] = index
        if not summary["candidateId"]:
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
        "executiveSummarySourceIds": generated.get("executiveSummarySourceIds", summary["sourceIds"][:3]),
        "businessReason": generated["businessReason"],
        "businessReasonSourceIds": generated.get("businessReasonSourceIds", summary["sourceIds"][:3]),
        "scores": summary["scores"],
        "ice": summary["ice"],
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


def _approved_rows_by_theme(rows: list[dict[str, str]], projects: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    theme_by_project = {project["ProjectID"]: project["ProjectTheme"] for project in projects}
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in _approved(rows):
        theme = theme_by_project.get(row["ProjectID"])
        if theme:
            grouped[theme].append(row)
    return grouped


def _approved_sources_by_theme(rows: list[dict[str, str]], projects: list[dict[str, str]], name_key: str, source_key: str) -> dict[str, dict[str, list[str]]]:
    theme_by_project = {project["ProjectID"]: project["ProjectTheme"] for project in projects}
    grouped: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
    for row in _approved(rows):
        theme = theme_by_project.get(row["ProjectID"])
        source_id = row.get(source_key)
        if theme and source_id:
            grouped[theme][row[name_key]].append(source_id)
    return grouped


def _top_counter_items(counter: Counter[str], limit: int, sources_by_name: dict[str, list[str]] | None = None) -> list[dict[str, Any]]:
    sources_by_name = sources_by_name or {}
    return [{"name": name, "occurrenceCount": count, "sourceIds": sources_by_name.get(name, [])} for name, count in counter.most_common(limit)]


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


def calculate_impact_score(metrics: dict[str, Any], ranges: dict[str, tuple[float, float]]) -> dict[str, Any]:
    factors = [
        _factor("winRate", "受注率", metrics.get("winRate"), _score_percent(metrics.get("winRate")), _format_percent(metrics.get("winRate"))),
        _factor("averageMarginRate", "平均利益率", metrics.get("averageMarginRate"), _score_percent(metrics.get("averageMarginRate")), _format_percent(metrics.get("averageMarginRate"))),
        _factor("wonRevenue", "受注売上", metrics.get("wonRevenue"), _score_minmax(metrics.get("wonRevenue"), ranges.get("wonRevenue", (0, 0))), _format_revenue(metrics.get("wonRevenue"))),
        _factor("averageEffortReductionRate", "平均工数削減率", metrics.get("averageEffortReductionRate"), _score_percent(metrics.get("averageEffortReductionRate")), _format_percent(metrics.get("averageEffortReductionRate"))),
        _factor("industryBreadth", "対象業種数", metrics.get("industryCount"), _score_minmax(metrics.get("industryCount"), ranges.get("industryCount", (0, 0))), f"{metrics.get('industryCount', 0)}業種"),
    ]
    score, weighted_factors = _weighted_axis(factors, IMPACT_WEIGHTS)
    return {
        "score": score,
        "summary": _impact_summary(metrics),
        "factors": weighted_factors,
    }


def calculate_confidence_score(metrics: dict[str, Any], ranges: dict[str, tuple[float, float]]) -> dict[str, Any]:
    support = metrics.get("supportingProjectCount")
    industries = metrics.get("industryCount")
    document_count = metrics.get("evidenceDocumentCount")
    expected_document_count = metrics.get("expectedDocumentCount") or 0
    document_coverage = _ratio_score(document_count, expected_document_count)
    factors = [
        _factor("evidenceVolume", "根拠案件数", support, _score_evidence_volume(support), f"{support or 0}案件"),
        _factor("industryDiversity", "業種多様性", industries, _score_industry_diversity(industries), f"{industries or 0}業種"),
        _factor("evidenceDocumentCoverage", "根拠文書カバレッジ", document_count, document_coverage, f"{document_count or 0}/{expected_document_count}文書"),
        _factor("commonPatternConsistency", "共通パターン一貫性", metrics.get("commonPatternConsistency"), _score_percent(metrics.get("commonPatternConsistency")), _format_percent(metrics.get("commonPatternConsistency"))),
        _factor("outcomeConsistency", "成功実績の一貫性", metrics.get("winRate"), _score_percent(metrics.get("winRate")), _format_percent(metrics.get("winRate"))),
        _factor("dataCompleteness", "データ完全性", metrics.get("dataCompleteness"), _score_percent(metrics.get("dataCompleteness")), _format_percent(metrics.get("dataCompleteness"))),
    ]
    score, weighted_factors = _weighted_axis(factors, CONFIDENCE_WEIGHTS)
    return {
        "score": score,
        "summary": _confidence_summary(metrics),
        "factors": weighted_factors,
    }


def calculate_ease_score(metrics: dict[str, Any], ranges: dict[str, tuple[float, float]]) -> dict[str, Any]:
    gap_burden = metrics.get("gapBurden")
    risk_burden = metrics.get("riskBurden")
    investment_level = metrics.get("investmentBurdenLevel")
    factors = [
        _factor("reusableAssetReadiness", "再利用可能資産の準備度", metrics.get("reusableAssetReadiness"), _score_percent(metrics.get("reusableAssetReadiness")), _format_percent(metrics.get("reusableAssetReadiness"))),
        _factor("standardizationReadiness", "標準化準備度", metrics.get("standardizationReadiness"), _score_percent(metrics.get("standardizationReadiness")), _format_percent(metrics.get("standardizationReadiness"))),
        _factor("inverseGapBurden", "標準化ギャップ負荷", gap_burden, _score_gap_burden(gap_burden), f"{gap_burden if gap_burden is not None else 'Unknown'}件"),
        _factor("inverseRiskBurden", "Highリスク負荷", risk_burden, _score_high_risk_burden(risk_burden), f"{risk_burden if risk_burden is not None else 'Unknown'}件"),
        _factor("inverseInvestmentBurden", "必要投資レベル", investment_level, _score_investment_burden(investment_level), f"{investment_level or 'Unknown'}={_score_investment_burden(investment_level)}"),
    ]
    score, weighted_factors = _weighted_axis(factors, EASE_WEIGHTS)
    score = _cap_ease_score(score, gap_burden, risk_burden, investment_level)
    return {
        "score": score,
        "summary": _ease_summary(metrics),
        "factors": weighted_factors,
    }


def calculate_normalized_ice_score(impact: int, confidence: int, ease: int) -> int:
    impact = _clamp(impact)
    confidence = _clamp(confidence)
    ease = _clamp(ease)
    normalized = ((impact / 100) * (confidence / 100) * (ease / 100)) ** (1 / 3)
    return _clamp(100 * normalized)


def _apply_ice_scores(summaries: list[dict[str, Any]]) -> None:
    ranges = _ice_ranges(summaries)
    for summary in summaries:
        metrics = summary["metrics"] | summary["iceInputs"]
        impact = calculate_impact_score(metrics, ranges)
        confidence = calculate_confidence_score(metrics, ranges)
        ease = calculate_ease_score(metrics, ranges)
        ice_score = calculate_normalized_ice_score(impact["score"], confidence["score"], ease["score"])
        summary["ice"] = {
            "score": ice_score,
            "impact": impact,
            "confidence": confidence,
            "ease": ease,
            "calculationMethod": "normalized-geometric-mean",
            "formulaVersion": "ice-v1",
        }
        summary["scores"]["priority"] = ice_score


def _ice_ranges(summaries: list[dict[str, Any]]) -> dict[str, tuple[float, float]]:
    keys = ["wonRevenue", "industryCount", "supportingProjectCount", "gapBurden", "riskBurden"]
    ranges: dict[str, tuple[float, float]] = {}
    for key in keys:
        values = [_number((summary["metrics"] | summary["iceInputs"]).get(key)) for summary in summaries]
        ranges[key] = (min(values), max(values)) if values else (0, 0)
    return ranges


def _fallback_generated_content(summary: dict[str, Any]) -> dict[str, Any]:
    theme = summary["theme"]
    current, next_model, future, rationale = BUSINESS_MODEL_BY_THEME.get(theme, ("Standard Offering", "Managed Service", "SaaS", "共通要件と再利用部品を段階的に標準化できる。"))
    candidate_sources = summary["sourceIds"][:3]
    asset_items = (summary["commonFeatures"] + summary["commonRequirements"])[:5]
    asset_sources = _merge_source_ids(asset_items, fallback=candidate_sources)
    risk_sources = _merge_source_ids(summary["commonRisks"][:3], fallback=candidate_sources)
    gap_sources = _merge_source_ids(summary["commonRequirements"][:3] + summary["commonRisks"][:2], fallback=candidate_sources)
    return {
        "name": summary["name"],
        "executiveSummary": f"ICE優先度 {summary['ice']['score']} の候補。Impact {summary['ice']['impact']['score']}、Confidence {summary['ice']['confidence']['score']}、Ease {summary['ice']['ease']['score']} をPython集計で算出した。",
        "executiveSummarySourceIds": candidate_sources,
        "businessReason": _ice_business_reason(summary),
        "businessReasonSourceIds": candidate_sources,
        "recommendedBusinessModel": {"current": current, "next": next_model, "futureOption": future, "rationale": rationale, "sourceIds": candidate_sources},
        "reusableAssets": [
            {
                "name": item["name"],
                "type": "Feature" if index < len(summary["commonFeatures"]) else "Requirement",
                "occurrenceCount": item["occurrenceCount"],
                "totalProjectCount": summary["metrics"]["supportingProjectCount"],
                "readinessScore": _clamp(item["occurrenceCount"] / summary["metrics"]["supportingProjectCount"] * 100),
                "currentState": "複数案件で利用実績あり",
                "nextAction": "標準テンプレート、設計ガイド、見積り前提へ整理する",
                "sourceIds": item.get("sourceIds") or candidate_sources,
            }
            for index, item in enumerate(asset_items)
        ],
        "standardizationGaps": [
            {"category": "Delivery", "currentState": "案件別に成果物粒度が異なる", "targetState": "標準スコープ、導入手順、完了条件を定義", "effort": "Medium", "priority": "High", "dependency": "営業・Delivery双方のレビュー", "sourceIds": gap_sources},
            {"category": "Operations", "currentState": "運用項目が案件ごとに分散", "targetState": "監視、評価、改善サイクルを標準メニュー化", "effort": "Medium", "priority": "Medium", "dependency": "運用責任範囲の明確化", "sourceIds": gap_sources},
        ],
        "successFactors": [
            {"text": "共通要件を標準スコープに固定する", "sourceIds": _merge_source_ids(summary["commonRequirements"][:3], fallback=candidate_sources)},
            {"text": "根拠文書を再利用可能な資産に整理する", "sourceIds": asset_sources},
            {"text": "案件固有対応の上限を定義する", "sourceIds": gap_sources},
        ],
        "failureFactors": [
            {"text": "案件固有要件を標準機能に混在させる", "sourceIds": gap_sources},
            {"text": "所有者と更新責任を決めない", "sourceIds": risk_sources},
            {"text": "運用フェーズの収益化を後回しにする", "sourceIds": candidate_sources},
        ],
        "risks": [
            {"name": item["name"], "impact": "Medium", "likelihood": "Medium", "mitigation": "標準化前に責任範囲、適用条件、除外条件を明記する", "sourceIds": item.get("sourceIds") or risk_sources}
            for item in summary["commonRisks"][:3]
        ],
        "managementDecision": {
            "decision": "標準化検討を開始し、90日以内に提供範囲と投資判断を確定する",
            "decisionSourceIds": gap_sources,
            "investmentLevel": "Medium",
            "timeHorizon": "90 days",
            "next90Days": [
                {"text": "再利用資産の棚卸しを完了する", "sourceIds": asset_sources},
                {"text": "標準スコープと除外条件を定義する", "sourceIds": gap_sources},
                {"text": "パイロット顧客候補を選定する", "sourceIds": candidate_sources},
            ],
            "successCriteria": [
                {"text": "標準提案テンプレートが完成", "sourceIds": gap_sources},
                {"text": "再利用資産の所有者が決定", "sourceIds": asset_sources},
                {"text": "次案件で再利用可能な見積り前提が承認", "sourceIds": candidate_sources},
            ],
            "stopOrReviewCriteria": [
                {"text": "標準化対象が2案件未満", "sourceIds": candidate_sources},
                {"text": "案件固有対応が主要工数を占める", "sourceIds": gap_sources},
                {"text": "運用責任範囲が合意できない", "sourceIds": risk_sources},
            ],
        },
    }


def _merge_source_ids(items: list[dict[str, Any]], fallback: list[str] | None = None) -> list[str]:
    source_ids = []
    for item in items:
        for source_id in item.get("sourceIds", []):
            if source_id not in source_ids:
                source_ids.append(source_id)
    return source_ids or (fallback or [])


def _number(value: str | int | float | None) -> float:
    if value in (None, "", "null"):
        return 0.0
    return float(value)


def _clamp(value: float) -> int:
    return max(0, min(100, int(round(value))))


def _factor(key: str, name: str, raw_value: Any, score: int | None, display_value: str) -> dict[str, Any]:
    return {"key": key, "name": name, "rawValue": raw_value, "score": score, "value": display_value}


def _weighted_axis(factors: list[dict[str, Any]], weights: dict[str, float]) -> tuple[int, list[dict[str, Any]]]:
    available = [factor for factor in factors if factor["score"] is not None]
    total_weight = sum(weights[factor["key"]] for factor in available)
    if not available or total_weight <= 0:
        return 0, []

    score = _clamp(sum(factor["score"] * (weights[factor["key"]] / total_weight) for factor in available))
    weighted_factors = []
    contribution_total = 0
    for index, factor in enumerate(available):
        contribution = _clamp(factor["score"] * (weights[factor["key"]] / total_weight))
        if index == len(available) - 1:
            contribution += score - (contribution_total + contribution)
        contribution_total += contribution
        weighted_factors.append({"name": factor["name"], "value": factor["value"], "contribution": contribution})
    return score, weighted_factors


def _score_percent(value: Any) -> int | None:
    if value in (None, ""):
        return None
    return _clamp(_number(value))


def _score_minmax(value: Any, value_range: tuple[float, float]) -> int | None:
    if value in (None, ""):
        return None
    minimum, maximum = value_range
    numeric = _number(value)
    if maximum == minimum:
        return 100 if numeric > 0 else 0
    return _clamp((numeric - minimum) / (maximum - minimum) * 100)


def _inverse_minmax_score(value: Any, value_range: tuple[float, float]) -> int | None:
    score = _score_minmax(value, value_range)
    return None if score is None else 100 - score


def _ratio_score(value: Any, denominator: Any) -> int | None:
    denominator_number = _number(denominator)
    if denominator_number <= 0:
        return None
    return _clamp(_number(value) / denominator_number * 100)


def _score_evidence_volume(value: Any) -> int | None:
    if value in (None, ""):
        return None
    count = int(_number(value))
    if count <= 0:
        return 0
    if count == 1:
        return 25
    if count == 2:
        return 50
    if count == 3:
        return 70
    if count == 4:
        return 80
    if count == 5:
        return 90
    return 100


def _score_industry_diversity(value: Any) -> int | None:
    if value in (None, ""):
        return None
    count = int(_number(value))
    if count <= 0:
        return 0
    if count == 1:
        return 40
    if count == 2:
        return 65
    if count == 3:
        return 80
    if count == 4:
        return 90
    return 100


def _score_gap_burden(value: Any) -> int | None:
    if value in (None, ""):
        return 50
    return _clamp(100 - (_number(value) * 35))


def _score_high_risk_burden(value: Any) -> int | None:
    if value in (None, ""):
        return 50
    return _clamp(100 - (_number(value) * 12.5))


def _score_investment_burden(value: Any) -> int | None:
    if value in (None, ""):
        return 50
    return BURDEN_LEVEL_SCORE.get(str(value), 50)


def _cap_ease_score(score: int, gap_burden: Any, risk_burden: Any, investment_level: Any) -> int:
    cap = 100
    risk_count = _number(risk_burden)
    gap_count = _number(gap_burden)
    if risk_burden in (None, "") or gap_burden in (None, "") or investment_level in (None, ""):
        cap = min(cap, 75)
    if risk_count >= 8:
        cap = min(cap, 55)
    elif risk_count >= 4:
        cap = min(cap, 70)
    if gap_count >= 2:
        cap = min(cap, 55)
    elif gap_count >= 1:
        cap = min(cap, 65)
    return min(score, cap)


def _format_percent(value: Any) -> str:
    return f"{_number(value):.1f}%"


def _format_revenue(value: Any) -> str:
    return f"{_number(value) / 100_000_000:.1f}億円"


def _common_pattern_consistency(patterns: list[dict[str, Any]], supporting_count: int) -> float:
    if supporting_count <= 0 or not patterns:
        return 0.0
    return round(mean(item["occurrenceCount"] / supporting_count * 100 for item in patterns), 1)


def _data_completeness(projects: list[dict[str, str]], financials: list[dict[str, str]], docs_by_project: dict[str, list[dict[str, Any]]]) -> float:
    checks = 0
    present = 0
    financials_by_project = {row["ProjectID"]: row for row in financials}
    project_fields = ["ProjectID", "Industry", "ProjectTheme", "WinLoss"]
    financial_fields = ["RevenueJPYMillion", "CostJPYMillion", "ProfitJPYMillion", "EffortReductionPct"]
    for project in projects:
        for field in project_fields:
            checks += 1
            present += 1 if project.get(field) not in (None, "") else 0
        financial = financials_by_project.get(project["ProjectID"], {})
        for field in financial_fields:
            checks += 1
            present += 1 if financial.get(field) not in (None, "") else 0
        checks += 1
        present += 1 if docs_by_project.get(project["ProjectID"]) else 0
    return round(present / checks * 100, 1) if checks else 0.0


def _standardization_gap_burden(*, lost_count: int, common_pattern_consistency: float, industry_count: int, supporting_count: int) -> int:
    burden = lost_count
    if common_pattern_consistency < 85:
        burden += 1
    if industry_count < supporting_count:
        burden += 1
    return burden


def _investment_burden_level(gap_burden: int, risk_burden: int, lost_count: int) -> str:
    if lost_count == 0 and gap_burden <= 1 and risk_burden <= 8:
        return "Low"
    if gap_burden <= 2 and risk_burden <= 10:
        return "Medium"
    return "High"


def _impact_summary(metrics: dict[str, Any]) -> str:
    return f"受注率{_format_percent(metrics.get('winRate'))}、平均利益率{_format_percent(metrics.get('averageMarginRate'))}、受注売上{_format_revenue(metrics.get('wonRevenue'))}から事業効果を評価。"


def _confidence_summary(metrics: dict[str, Any]) -> str:
    return f"{metrics.get('supportingProjectCount', 0)}案件・{metrics.get('industryCount', 0)}業種、根拠文書{metrics.get('evidenceDocumentCount', 0)}件、受注率{_format_percent(metrics.get('winRate'))}から分析確信度を評価。"


def _ease_summary(metrics: dict[str, Any]) -> str:
    return f"再利用準備度{_format_percent(metrics.get('reusableAssetReadiness'))}、ギャップ負荷{metrics.get('gapBurden', 0)}件、Highリスク{metrics.get('riskBurden', 0)}件、必要投資レベル{metrics.get('investmentBurdenLevel', 'Unknown')}から実行容易性を保守的に評価。"


def _ice_business_reason(summary: dict[str, Any]) -> str:
    metrics = summary["metrics"]
    ice = summary["ice"]
    return (
        f"{metrics['industryCount']}業種・{metrics['supportingProjectCount']}案件で共通構成が確認され、"
        f"受注率{metrics['winRate']:.1f}%、平均利益率{metrics['averageMarginRate']:.1f}%、受注売上{metrics['wonRevenue'] / 100_000_000:.1f}億円からImpactは{ice['impact']['score']}です。"
        f"根拠件数、業種多様性、受注実績の一貫性からConfidenceは{ice['confidence']['score']}、標準化ギャップとHighリスクを踏まえたEaseは{ice['ease']['score']}です。"
        f"3軸を掛け合わせたICE優先度が{ice['score']}のため、事業化候補として優先検討できます。"
    )
