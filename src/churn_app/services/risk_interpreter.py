"""Deterministic interpretation of an already assigned churn risk level.

This module consumes prediction evidence and a supplied `RiskLevel`. It
validates their consistency and returns presentation-neutral explanatory
content. It does not execute models, run the decision policy, generate
recommendations, or render UI.
"""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType

from churn_app.domain import (
    InterpretationResult,
    ModelPrediction,
    ModelRole,
    ModelType,
    PredictionResult,
    RiskLevel,
)

_VALID_CLASSES = frozenset({0, 1})

# Validation mirror of the canonical feature table in
# docs/features/churn-risk-orchestration.md. The feature specification remains
# the normative owner of the decision semantics.
_EXPECTED_RISK_BY_CLASSES = MappingProxyType(
    {
        (0, 0): RiskLevel.LOW,
        (0, 1): RiskLevel.MODERATE,
        (1, 0): RiskLevel.HIGH,
        (1, 1): RiskLevel.CRITICAL,
    }
)

_INTERPRETATIONS = MappingProxyType(
    {
        RiskLevel.LOW: (
            "Low Churn Risk",
            "No consistent indication of customer churn was detected.",
            "Both models predicted customer retention.",
            (
                "Neither model detected churn.",
                "The models agree on customer retention.",
                "The evidence does not indicate elevated churn risk.",
            ),
        ),
        RiskLevel.MODERATE: (
            "Moderate Churn Risk",
            "The complementary model detected a churn signal that was not confirmed by the primary model.",
            "Only the complementary model predicted churn.",
            (
                "The primary model remained negative.",
                "The complementary model detected churn.",
                "This disagreement corresponds to moderate churn risk.",
            ),
        ),
        RiskLevel.HIGH: (
            "High Churn Risk",
            "The primary prediction model detected evidence associated with customer churn.",
            "Only the primary model predicted churn.",
            (
                "The primary model detected churn.",
                "The complementary model did not confirm the prediction.",
                "This disagreement corresponds to high churn risk.",
            ),
        ),
        RiskLevel.CRITICAL: (
            "Critical Churn Risk",
            "Independent predictive models consistently detected customer churn indicators.",
            "Both models independently predicted churn.",
            (
                "Both models detected churn.",
                "The evidence is mutually reinforcing.",
                "This agreement corresponds to critical churn risk.",
            ),
        ),
    }
)


class RiskInterpreterError(Exception):
    """Base exception for deterministic risk interpretation failures."""


class InvalidInterpretationInputError(RiskInterpreterError):
    """Raised when interpreter inputs violate expected domain contracts."""


class InterpretationConsistencyError(RiskInterpreterError):
    """Raised when predictions and the supplied risk level are inconsistent."""

    def __init__(
        self,
        combination: tuple[int, int],
        supplied_risk_level: RiskLevel,
        expected_risk_level: RiskLevel,
    ) -> None:
        self.combination = combination
        self.supplied_risk_level = supplied_risk_level
        self.expected_risk_level = expected_risk_level
        super().__init__(
            "PredictionResult and RiskLevel are inconsistent: "
            f"combination={combination!r}, supplied={supplied_risk_level.value}, "
            f"expected={expected_risk_level.value}"
        )


@dataclass(frozen=True, slots=True)
class _InterpretationTemplate:
    title: str
    summary: str
    model_agreement: str
    rationale: tuple[str, ...]


def interpret_risk(
    prediction_result: PredictionResult,
    risk_level: RiskLevel,
) -> InterpretationResult:
    """Explain a supplied risk level using independent model predictions."""
    _validate_prediction_result(prediction_result)
    _validate_risk_level(risk_level)

    gradient_boosting_class = _validated_class(
        "gradient_boosting",
        prediction_result.gradient_boosting.predicted_class,
    )
    decision_tree_class = _validated_class(
        "decision_tree",
        prediction_result.decision_tree.predicted_class,
    )
    combination = (gradient_boosting_class, decision_tree_class)
    expected_risk_level = _EXPECTED_RISK_BY_CLASSES[combination]
    if risk_level is not expected_risk_level:
        raise InterpretationConsistencyError(
            combination=combination,
            supplied_risk_level=risk_level,
            expected_risk_level=expected_risk_level,
        )

    template = _template_for(risk_level)
    return InterpretationResult(
        risk_level=risk_level,
        title=template.title,
        summary=template.summary,
        model_agreement=template.model_agreement,
        evidence=_evidence(gradient_boosting_class, decision_tree_class),
        rationale=template.rationale,
    )


def _validate_prediction_result(prediction_result: object) -> None:
    if type(prediction_result) is not PredictionResult:
        raise InvalidInterpretationInputError(
            "prediction_result must be a PredictionResult."
        )
    if type(prediction_result.gradient_boosting) is not ModelPrediction:
        raise InvalidInterpretationInputError(
            "prediction_result.gradient_boosting must be a ModelPrediction."
        )
    if type(prediction_result.decision_tree) is not ModelPrediction:
        raise InvalidInterpretationInputError(
            "prediction_result.decision_tree must be a ModelPrediction."
        )
    _validate_model_identity(
        field_name="gradient_boosting",
        prediction=prediction_result.gradient_boosting,
        expected_model_type=ModelType.GRADIENT_BOOSTING,
        expected_role=ModelRole.PRIMARY,
    )
    _validate_model_identity(
        field_name="decision_tree",
        prediction=prediction_result.decision_tree,
        expected_model_type=ModelType.DECISION_TREE,
        expected_role=ModelRole.SENSITIVITY_COMPLEMENT,
    )


def _validate_risk_level(risk_level: object) -> None:
    if type(risk_level) is not RiskLevel:
        raise InvalidInterpretationInputError("risk_level must be a RiskLevel.")


def _validated_class(model_name: str, predicted_class: object) -> int:
    if isinstance(predicted_class, bool) or not isinstance(predicted_class, int):
        raise InvalidInterpretationInputError(
            f"invalid predicted class for {model_name}: {predicted_class!r}"
        )
    if predicted_class not in _VALID_CLASSES:
        raise InvalidInterpretationInputError(
            f"invalid predicted class for {model_name}: {predicted_class!r}"
        )
    return predicted_class


def _validate_model_identity(
    *,
    field_name: str,
    prediction: ModelPrediction,
    expected_model_type: ModelType,
    expected_role: ModelRole,
) -> None:
    if prediction.model.model_type is not expected_model_type:
        raise InvalidInterpretationInputError(
            f"{field_name} must contain {expected_model_type.value} prediction."
        )
    if prediction.model.role is not expected_role:
        raise InvalidInterpretationInputError(
            f"{field_name} must have role {expected_role.value}."
        )


def _template_for(risk_level: RiskLevel) -> _InterpretationTemplate:
    title, summary, model_agreement, rationale = _INTERPRETATIONS[risk_level]
    return _InterpretationTemplate(
        title=title,
        summary=summary,
        model_agreement=model_agreement,
        rationale=rationale,
    )


def _evidence(
    gradient_boosting_class: int,
    decision_tree_class: int,
) -> tuple[str, ...]:
    return (
        f"Gradient Boosting predicted {_class_label(gradient_boosting_class)}.",
        f"Decision Tree predicted {_class_label(decision_tree_class)}.",
    )


def _class_label(predicted_class: int) -> str:
    if predicted_class == 1:
        return "churn"
    return "retention"
