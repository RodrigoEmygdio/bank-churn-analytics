"""Composition boundary for presentation-ready business output.

This module copies existing interpretation and recommendation contracts into a
single immutable `PresentationResult`. It performs no business reasoning,
text generation, rendering, or formatting.
"""

from __future__ import annotations

from churn_app.domain import (
    InterpretationResult,
    PresentationResult,
    RecommendationResult,
    RiskLevel,
)


class PresentationLayerError(Exception):
    """Base exception for deterministic presentation-layer failures."""


class InvalidPresentationInputError(PresentationLayerError):
    """Raised when presentation inputs violate expected domain contracts."""


class PresentationConsistencyError(PresentationLayerError):
    """Raised when interpretation and recommendation risk levels differ."""

    def __init__(
        self,
        interpretation: InterpretationResult,
        recommendation: RecommendationResult,
    ) -> None:
        self.interpretation_risk_level = interpretation.risk_level
        self.recommendation_risk_level = recommendation.risk_level
        super().__init__(
            "InterpretationResult and RecommendationResult risk levels differ: "
            f"interpretation={interpretation.risk_level.value}, "
            f"recommendation={recommendation.risk_level.value}"
        )


def build_presentation(
    interpretation: InterpretationResult,
    recommendation: RecommendationResult,
) -> PresentationResult:
    """Compose interpretation and recommendation into one immutable contract."""
    _validate_interpretation(interpretation)
    _validate_recommendation(recommendation)
    if interpretation.risk_level is not recommendation.risk_level:
        raise PresentationConsistencyError(interpretation, recommendation)

    return PresentationResult(
        risk_level=interpretation.risk_level,
        title=interpretation.title,
        summary=interpretation.summary,
        model_agreement=interpretation.model_agreement,
        evidence=interpretation.evidence,
        rationale=interpretation.rationale,
        recommendation_priority=recommendation.priority,
        objective=recommendation.objective,
        recommendations=recommendation.recommendations,
        expected_outcome=recommendation.expected_outcome,
    )


def _validate_interpretation(interpretation: object) -> None:
    if type(interpretation) is not InterpretationResult:
        raise InvalidPresentationInputError(
            "interpretation must be an InterpretationResult."
        )
    if type(interpretation.risk_level) is not RiskLevel:
        raise InvalidPresentationInputError(
            "interpretation.risk_level must be a RiskLevel."
        )


def _validate_recommendation(recommendation: object) -> None:
    if type(recommendation) is not RecommendationResult:
        raise InvalidPresentationInputError(
            "recommendation must be a RecommendationResult."
        )
    if type(recommendation.risk_level) is not RiskLevel:
        raise InvalidPresentationInputError(
            "recommendation.risk_level must be a RiskLevel."
        )
