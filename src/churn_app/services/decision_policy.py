"""Pure four-level decision policy for independent model predictions.

This module maps Gradient Boosting and Decision Tree predicted classes to the
approved risk levels. It does not inspect probabilities, load artifacts,
execute models, or produce user-facing interpretation text.
"""

from __future__ import annotations

from types import MappingProxyType

from churn_app.domain import ModelPrediction, RiskLevel

_POLICY = MappingProxyType(
    {
        (0, 0): RiskLevel.LOW,
        (0, 1): RiskLevel.ATTENTION,
        (1, 0): RiskLevel.HIGH,
        (1, 1): RiskLevel.CRITICAL,
    }
)


def determine_risk_level(
    gradient_boosting: ModelPrediction, decision_tree: ModelPrediction
) -> RiskLevel:
    """Determine the approved consolidated risk level from model classes."""
    return _POLICY[(gradient_boosting.predicted_class, decision_tree.predicted_class)]
