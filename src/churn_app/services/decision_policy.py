"""Pure decision policy for independent model predictions.

This module maps Gradient Boosting and Decision Tree predicted classes to the
approved risk level. It does not inspect probabilities, load artifacts,
execute models, interpret results, or render UI.
"""

from __future__ import annotations

from types import MappingProxyType

from churn_app.domain import PredictionResult, RiskLevel

_VALID_CLASSES = frozenset({0, 1})
_POLICY = MappingProxyType(
    {
        (0, 0): RiskLevel.LOW,
        (0, 1): RiskLevel.MODERATE,
        (1, 0): RiskLevel.HIGH,
        (1, 1): RiskLevel.CRITICAL,
    }
)


class DecisionPolicyError(Exception):
    """Base exception for deterministic decision-policy failures."""


class InvalidDecisionInputError(DecisionPolicyError):
    """Raised when model classes are malformed or unsupported."""

    def __init__(self, model_name: str, predicted_class: object) -> None:
        self.model_name = model_name
        self.predicted_class = predicted_class
        super().__init__(
            f"invalid predicted class for {model_name}: {predicted_class!r}"
        )


class UnsupportedDecisionCombinationError(DecisionPolicyError):
    """Raised when validated classes do not match an approved policy entry."""

    def __init__(self, combination: tuple[int, int]) -> None:
        self.combination = combination
        super().__init__(f"unsupported decision combination: {combination!r}")


def determine_risk_level(prediction_result: PredictionResult) -> RiskLevel:
    """Apply the approved four-level policy to independent model classes."""
    gradient_boosting_class = _validated_class(
        "gradient_boosting",
        prediction_result.gradient_boosting.predicted_class,
    )
    decision_tree_class = _validated_class(
        "decision_tree",
        prediction_result.decision_tree.predicted_class,
    )
    combination = (gradient_boosting_class, decision_tree_class)

    try:
        return _POLICY[combination]
    except KeyError as exc:
        raise UnsupportedDecisionCombinationError(combination) from exc


def _validated_class(model_name: str, predicted_class: object) -> int:
    if isinstance(predicted_class, bool) or not isinstance(predicted_class, int):
        raise InvalidDecisionInputError(model_name, predicted_class)
    if predicted_class not in _VALID_CLASSES:
        raise InvalidDecisionInputError(model_name, predicted_class)
    return predicted_class
