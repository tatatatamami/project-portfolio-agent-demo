from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class LoadedData:
    customers: list[dict[str, str]]
    projects: list[dict[str, str]]
    opportunities: list[dict[str, str]]
    proposals: list[dict[str, str]]
    requirements: list[dict[str, str]]
    risks: list[dict[str, str]]
    features: list[dict[str, str]]
    financials: list[dict[str, str]]
    outcomes: list[dict[str, str]]
    documents: list[dict[str, Any]]
    expected_metrics: dict[str, Any]
    validation_rules: dict[str, Any]


@dataclass(frozen=True)
class ValidationIssue:
    severity: str
    code: str
    message: str
    context: dict[str, Any] | None = None
