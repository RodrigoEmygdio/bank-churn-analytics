"""Deterministic business recommendations from risk interpretation.

This module consumes an `InterpretationResult` and returns presentation-neutral
business recommendations. It does not predict, classify, interpret risk,
inspect model evidence, or render UI.
"""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType

from churn_app.domain import (
    InterpretationResult,
    RecommendationPriority,
    RecommendationResult,
    RiskLevel,
)

_RECOMMENDATIONS = MappingProxyType(
    {
        RiskLevel.LOW: (
            RecommendationPriority.LOW,
            "Maintain customer relationship.",
            (
                "Continue periodic monitoring.",
                "Maintain current customer engagement.",
                "No immediate retention action is required.",
            ),
            "Customer relationship remains stable through normal monitoring.",
        ),
        RiskLevel.MODERATE: (
            RecommendationPriority.MEDIUM,
            "Investigate potential early churn indicators.",
            (
                "Review recent customer activity.",
                "Monitor account behavior.",
                "Consider proactive customer contact if additional indicators emerge.",
            ),
            "Potential churn indicators are assessed before escalation.",
        ),
        RiskLevel.HIGH: (
            RecommendationPriority.HIGH,
            "Reduce customer churn risk through proactive engagement.",
            (
                "Contact the customer.",
                "Review customer satisfaction.",
                "Evaluate appropriate retention actions.",
            ),
            "Customer retention opportunities are identified before churn occurs.",
        ),
        RiskLevel.CRITICAL: (
            RecommendationPriority.URGENT,
            "Execute immediate customer retention strategy.",
            (
                "Initiate urgent retention campaign.",
                "Escalate to customer success team.",
                "Prioritize executive follow-up if applicable.",
            ),
            "Immediate intervention maximizes retention opportunity.",
        ),
    }
)


class RecommendationEngineError(Exception):
    """Base exception for deterministic recommendation-engine failures."""


class InvalidRecommendationInputError(RecommendationEngineError):
    """Raised when recommendation inputs violate expected domain contracts."""


@dataclass(frozen=True, slots=True)
class _RecommendationTemplate:
    priority: RecommendationPriority
    objective: str
    recommendations: tuple[str, ...]
    expected_outcome: str


def generate_recommendation(
    interpretation: InterpretationResult,
) -> RecommendationResult:
    """Generate deterministic business recommendations for an interpretation."""
    _validate_interpretation(interpretation)
    template = _template_for(interpretation.risk_level)
    return RecommendationResult(
        risk_level=interpretation.risk_level,
        priority=template.priority,
        objective=template.objective,
        recommendations=template.recommendations,
        expected_outcome=template.expected_outcome,
    )


def _validate_interpretation(interpretation: object) -> None:
    if type(interpretation) is not InterpretationResult:
        raise InvalidRecommendationInputError(
            "interpretation must be an InterpretationResult."
        )
    if type(interpretation.risk_level) is not RiskLevel:
        raise InvalidRecommendationInputError(
            "interpretation.risk_level must be a RiskLevel."
        )
    if interpretation.risk_level not in _RECOMMENDATIONS:
        raise InvalidRecommendationInputError(
            f"no recommendation mapping for {interpretation.risk_level!r}."
        )


def _template_for(risk_level: RiskLevel) -> _RecommendationTemplate:
    priority, objective, recommendations, expected_outcome = _RECOMMENDATIONS[
        risk_level
    ]
    return _RecommendationTemplate(
        priority=priority,
        objective=objective,
        recommendations=recommendations,
        expected_outcome=expected_outcome,
    )
