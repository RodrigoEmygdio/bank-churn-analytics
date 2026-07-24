"""Presentation-ready contracts independent from UI frameworks.

These contracts aggregate existing business-domain outputs without formatting,
styling, or rendering concerns.
"""

from __future__ import annotations

from dataclasses import dataclass

from churn_app.domain.recommendation import RecommendationPriority
from churn_app.domain.risk_level import RiskLevel


@dataclass(frozen=True, slots=True)
class PresentationResult:
    """Single immutable contract consumed by future UI rendering."""

    risk_level: RiskLevel
    title: str
    summary: str
    model_agreement: str
    evidence: tuple[str, ...]
    rationale: tuple[str, ...]
    recommendation_priority: RecommendationPriority
    objective: str
    recommendations: tuple[str, ...]
    expected_outcome: str
