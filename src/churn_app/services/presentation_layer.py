"""Composition boundary for presentation-ready business output.

This module copies existing prediction, interpretation, and recommendation
contracts into a single immutable `PresentationResult`. It performs no risk
calculation, text generation, rendering, or formatting.
"""

from __future__ import annotations

import math

from churn_app.domain import (
    InterpretationResult,
    ModelPrediction,
    ModelPresentationResult,
    PredictionResult,
    PresentationResult,
    RecommendationResult,
    RiskLevel,
)

_PREDICTED_LABELS = {
    0: "Retention",
    1: "Churn",
}


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
    prediction: PredictionResult,
    interpretation: InterpretationResult,
    recommendation: RecommendationResult,
) -> PresentationResult:
    """Compose prediction, interpretation, and recommendation into one contract."""
    _validate_prediction(prediction)
    _validate_interpretation(interpretation)
    _validate_recommendation(recommendation)
    if interpretation.risk_level is not recommendation.risk_level:
        raise PresentationConsistencyError(interpretation, recommendation)

    return PresentationResult(
        risk_level=interpretation.risk_level,
        title=interpretation.title,
        summary=interpretation.summary,
        gradient_boosting=_build_model_presentation(prediction.gradient_boosting),
        decision_tree=_build_model_presentation(prediction.decision_tree),
        model_agreement=interpretation.model_agreement,
        evidence=interpretation.evidence,
        rationale=interpretation.rationale,
        recommendation_priority=recommendation.priority,
        objective=recommendation.objective,
        recommendations=recommendation.recommendations,
        expected_outcome=recommendation.expected_outcome,
    )


def _validate_prediction(prediction: object) -> None:
    if type(prediction) is not PredictionResult:
        raise InvalidPresentationInputError("prediction must be a PredictionResult.")
    _validate_model_prediction("gradient_boosting", prediction.gradient_boosting)
    _validate_model_prediction("decision_tree", prediction.decision_tree)


def _validate_model_prediction(model_name: str, prediction: object) -> None:
    if type(prediction) is not ModelPrediction:
        raise InvalidPresentationInputError(f"{model_name} must be a ModelPrediction.")
    if (
        isinstance(prediction.predicted_class, bool)
        or not isinstance(prediction.predicted_class, int)
        or prediction.predicted_class not in _PREDICTED_LABELS
    ):
        raise InvalidPresentationInputError(
            f"{model_name}.predicted_class must be integer 0 or 1."
        )
    probability = prediction.probability
    if probability is None:
        return
    if isinstance(probability, bool) or not isinstance(probability, int | float):
        raise InvalidPresentationInputError(
            f"{model_name}.probability must be a number between 0.0 and 1.0."
        )
    if not math.isfinite(float(probability)) or not 0.0 <= float(probability) <= 1.0:
        raise InvalidPresentationInputError(
            f"{model_name}.probability must be a number between 0.0 and 1.0."
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


def _build_model_presentation(
    prediction: ModelPrediction,
) -> ModelPresentationResult:
    return ModelPresentationResult(
        display_name=prediction.model.display_name,
        predicted_class=prediction.predicted_class,
        predicted_label=_PREDICTED_LABELS[prediction.predicted_class],
        churn_probability=prediction.probability,
    )
