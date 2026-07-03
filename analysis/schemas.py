from __future__ import annotations

from typing import Any


DASHBOARD_DATA_SCHEMA: dict[str, Any] = {
    "required": ["analysisRun", "dashboardSummary", "candidates"],
    "properties": {
        "analysisRun": {"required": ["runId", "status", "generatedAt", "sourceProjectCount", "modelProvider", "modelDeployment", "promptVersion"]},
        "dashboardSummary": {"required": ["projectCount", "candidateCount", "wonRevenue", "averageMarginRate"]},
        "candidates": {
            "itemRequired": [
                "candidateId",
                "rank",
                "name",
                "executiveSummary",
                "businessReason",
                "scores",
                "ice",
                "metrics",
                "recommendedBusinessModel",
                "supportingProjects",
                "reusableAssets",
                "standardizationGaps",
                "successFactors",
                "failureFactors",
                "risks",
                "managementDecision",
            ]
        },
    },
}


LLM_RESPONSE_JSON_SCHEMA: dict[str, Any] = {
    "type": "json_schema",
    "json_schema": {
        "name": "portfolio_candidate_analysis",
        "strict": True,
        "schema": {
            "type": "object",
            "additionalProperties": False,
            "required": [
                "name",
                "executiveSummary",
                "executiveSummarySourceIds",
                "businessReason",
                "businessReasonSourceIds",
                "recommendedBusinessModel",
                "reusableAssets",
                "standardizationGaps",
                "successFactors",
                "failureFactors",
                "risks",
                "managementDecision",
            ],
            "properties": {
                "name": {"type": "string"},
                "executiveSummary": {"type": "string"},
                "executiveSummarySourceIds": {"type": "array", "items": {"type": "string"}},
                "businessReason": {"type": "string"},
                "businessReasonSourceIds": {"type": "array", "items": {"type": "string"}},
                "recommendedBusinessModel": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["current", "next", "futureOption", "rationale", "sourceIds"],
                    "properties": {
                        "current": {"type": "string"},
                        "next": {"type": "string"},
                        "futureOption": {"type": "string"},
                        "rationale": {"type": "string"},
                        "sourceIds": {"type": "array", "items": {"type": "string"}},
                    },
                },
                "reusableAssets": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["name", "type", "occurrenceCount", "totalProjectCount", "readinessScore", "currentState", "nextAction", "sourceIds"],
                        "properties": {
                            "name": {"type": "string"},
                            "type": {"type": "string"},
                            "occurrenceCount": {"type": "integer"},
                            "totalProjectCount": {"type": "integer"},
                            "readinessScore": {"type": "integer", "minimum": 0, "maximum": 100},
                            "currentState": {"type": "string"},
                            "nextAction": {"type": "string"},
                            "sourceIds": {"type": "array", "items": {"type": "string"}},
                        },
                    },
                },
                "standardizationGaps": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["category", "currentState", "targetState", "effort", "priority", "dependency", "sourceIds"],
                        "properties": {
                            "category": {"type": "string"},
                            "currentState": {"type": "string"},
                            "targetState": {"type": "string"},
                            "effort": {"type": "string"},
                            "priority": {"type": "string"},
                            "dependency": {"type": "string"},
                            "sourceIds": {"type": "array", "items": {"type": "string"}},
                        },
                    },
                },
                "successFactors": {"type": "array", "items": {"$ref": "#/$defs/evidenceText"}},
                "failureFactors": {"type": "array", "items": {"$ref": "#/$defs/evidenceText"}},
                "risks": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["name", "impact", "likelihood", "mitigation", "sourceIds"],
                        "properties": {
                            "name": {"type": "string"},
                            "impact": {"type": "string"},
                            "likelihood": {"type": "string"},
                            "mitigation": {"type": "string"},
                            "sourceIds": {"type": "array", "items": {"type": "string"}},
                        },
                    },
                },
                "managementDecision": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["decision", "decisionSourceIds", "investmentLevel", "timeHorizon", "next90Days", "successCriteria", "stopOrReviewCriteria"],
                    "properties": {
                        "decision": {"type": "string"},
                        "decisionSourceIds": {"type": "array", "items": {"type": "string"}},
                        "investmentLevel": {"type": "string"},
                        "timeHorizon": {"type": "string"},
                        "next90Days": {"type": "array", "items": {"$ref": "#/$defs/evidenceText"}},
                        "successCriteria": {"type": "array", "items": {"$ref": "#/$defs/evidenceText"}},
                        "stopOrReviewCriteria": {"type": "array", "items": {"$ref": "#/$defs/evidenceText"}},
                    },
                },
            },
            "$defs": {
                "evidenceText": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["text", "sourceIds"],
                    "properties": {
                        "text": {"type": "string"},
                        "sourceIds": {"type": "array", "items": {"type": "string"}},
                    },
                }
            },
        },
    },
}


def validate_required_shape(document: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for key in DASHBOARD_DATA_SCHEMA["required"]:
        if key not in document:
            errors.append(f"Missing top-level field: {key}")
    for section, spec in DASHBOARD_DATA_SCHEMA["properties"].items():
        if section not in document:
            continue
        if section == "candidates":
            for index, candidate in enumerate(document[section]):
                for key in spec["itemRequired"]:
                    if key not in candidate:
                        errors.append(f"Missing candidates[{index}].{key}")
        else:
            for key in spec.get("required", []):
                if key not in document[section]:
                    errors.append(f"Missing {section}.{key}")
    return errors
