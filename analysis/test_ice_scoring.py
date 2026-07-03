from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from data_loader import load_portfolio_data
from metrics import (
    build_dashboard_candidate,
    build_metrics,
    calculate_confidence_score,
    calculate_ease_score,
    calculate_impact_score,
    calculate_normalized_ice_score,
)


class IceScoringTests(unittest.TestCase):
    def test_normalized_ice_calculation(self) -> None:
        self.assertEqual(100, calculate_normalized_ice_score(100, 100, 100))
        self.assertEqual(46, calculate_normalized_ice_score(100, 100, 10))
        self.assertLess(calculate_normalized_ice_score(100, 100, 10), calculate_normalized_ice_score(80, 80, 80))

    def test_impact_calculation_uses_weighted_available_factors(self) -> None:
        metrics = {
            "winRate": 100,
            "averageMarginRate": 32,
            "wonRevenue": 2_190_000_000,
            "averageEffortReductionRate": 35.8,
            "industryCount": 4,
        }
        score = calculate_impact_score(metrics, {"wonRevenue": (1_000_000_000, 2_190_000_000), "industryCount": (1, 4)})

        self.assertGreaterEqual(score["score"], 70)
        self.assertEqual("受注率", score["factors"][0]["name"])
        self.assertEqual("100.0%", score["factors"][0]["value"])

    def test_confidence_calculation(self) -> None:
        score = calculate_confidence_score(
            {
                "supportingProjectCount": 4,
                "industryCount": 4,
                "evidenceDocumentCount": 12,
                "expectedDocumentCount": 12,
                "commonPatternConsistency": 100,
                "winRate": 100,
                "dataCompleteness": 100,
            },
            {"supportingProjectCount": (1, 4), "industryCount": (1, 4)},
        )

        self.assertEqual(94, score["score"])
        self.assertTrue(any(factor["name"] == "根拠案件数" and factor["value"] == "4案件" for factor in score["factors"]))
        self.assertTrue(any(factor["name"] == "業種多様性" and factor["value"] == "4業種" for factor in score["factors"]))
        self.assertTrue(any(factor["name"] == "成功実績の一貫性" for factor in score["factors"]))
        self.assertTrue(any(factor["name"] == "データ完全性" for factor in score["factors"]))

    def test_confidence_reflects_outcome_consistency(self) -> None:
        score = calculate_confidence_score(
            {
                "supportingProjectCount": 4,
                "industryCount": 4,
                "evidenceDocumentCount": 12,
                "expectedDocumentCount": 12,
                "commonPatternConsistency": 100,
                "winRate": 75,
                "dataCompleteness": 100,
            },
            {"supportingProjectCount": (1, 4), "industryCount": (1, 4)},
        )

        self.assertEqual(90, score["score"])

    def test_ease_calculation(self) -> None:
        score = calculate_ease_score(
            {
                "reusableAssetReadiness": 100,
                "standardizationReadiness": 96,
                "gapBurden": 0,
                "riskBurden": 8,
                "investmentBurdenLevel": "Low",
            },
            {"gapBurden": (0, 2), "riskBurden": (8, 10)},
        )

        self.assertEqual(55, score["score"])
        self.assertTrue(any(factor["name"] == "必要投資レベル" for factor in score["factors"]))

    def test_ease_uses_conservative_unknown_values(self) -> None:
        score = calculate_ease_score(
            {
                "reusableAssetReadiness": 100,
                "standardizationReadiness": 100,
                "gapBurden": None,
                "riskBurden": None,
                "investmentBurdenLevel": None,
            },
            {},
        )

        self.assertEqual(75, score["score"])
        self.assertTrue(any(factor["name"] == "必要投資レベル" and factor["value"] == "Unknown=50" for factor in score["factors"]))

    def test_missing_items_renormalize_weights(self) -> None:
        score = calculate_impact_score(
            {"winRate": 100, "averageMarginRate": None, "wonRevenue": None, "averageEffortReductionRate": None, "industryCount": None},
            {},
        )

        self.assertEqual(100, score["score"])
        self.assertEqual(1, len(score["factors"]))

    def test_dry_run_and_llm_path_keep_same_ice_scores(self) -> None:
        data = load_portfolio_data(Path(__file__).parents[1] / "test-data")
        calculated = build_metrics(data)
        dry_run = [build_dashboard_candidate(candidate) for candidate in calculated["candidates"]]
        llm_payload = {
            "name": "LLM name",
            "executiveSummary": "LLM summary",
            "businessReason": "LLM reason",
            "recommendedBusinessModel": {"current": "Standard Offering", "next": "Managed Service", "futureOption": "SaaS", "rationale": "rationale"},
            "reusableAssets": [],
            "standardizationGaps": [],
            "successFactors": [],
            "failureFactors": [],
            "risks": [],
            "managementDecision": {"decision": "decide", "investmentLevel": "Medium", "timeHorizon": "90 days", "next90Days": [], "successCriteria": [], "stopOrReviewCriteria": []},
        }
        llm_run = [build_dashboard_candidate(candidate, llm_payload) for candidate in calculated["candidates"]]

        self.assertEqual([candidate["ice"] for candidate in dry_run], [candidate["ice"] for candidate in llm_run])
        self.assertEqual([candidate["scores"]["priority"] for candidate in dry_run], [candidate["ice"]["score"] for candidate in dry_run])

    def test_rank_tie_breaker_uses_impact_confidence_ease_candidate_id(self) -> None:
        candidates = [
            {"candidateId": "B", "ice": {"score": 90, "impact": {"score": 80}, "confidence": {"score": 90}, "ease": {"score": 90}}},
            {"candidateId": "A", "ice": {"score": 90, "impact": {"score": 80}, "confidence": {"score": 90}, "ease": {"score": 90}}},
            {"candidateId": "C", "ice": {"score": 90, "impact": {"score": 85}, "confidence": {"score": 80}, "ease": {"score": 90}}},
        ]

        ordered = sorted(candidates, key=lambda item: (-item["ice"]["score"], -item["ice"]["impact"]["score"], -item["ice"]["confidence"]["score"], -item["ice"]["ease"]["score"], item["candidateId"]))

        self.assertEqual(["C", "A", "B"], [candidate["candidateId"] for candidate in ordered])


if __name__ == "__main__":
    unittest.main()
