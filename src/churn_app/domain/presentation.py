"""Presentation-ready contracts independent from UI frameworks.

These contracts aggregate existing business-domain outputs without formatting,
styling, or rendering concerns.
"""

from __future__ import annotations

from dataclasses import dataclass

from churn_app.domain.recommendation import RecommendationPriority
from churn_app.domain.risk_level import RiskLevel


@dataclass(frozen=True, slots=True)
class ModelPresentationResult:
    """Presentation-neutral output for one independent model prediction.

    `churn_probability` is the model-specific positive churn-class probability.
    It is not a confidence score and must not be combined with another model's
    probability.
    """

    display_name: str
    predicted_class: int
    predicted_label: str
    churn_probability: float | None


@dataclass(frozen=True, slots=True)
class PresentationResult:
    """Single immutable contract consumed by UI rendering."""

    risk_level: RiskLevel
    title: str
    summary: str
    gradient_boosting: ModelPresentationResult
    decision_tree: ModelPresentationResult
    model_agreement: str
    evidence: tuple[str, ...]
    rationale: tuple[str, ...]
    recommendation_priority: RecommendationPriority
    objective: str
    recommendations: tuple[str, ...]
    expected_outcome: str
