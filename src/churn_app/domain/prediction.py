"""Prediction domain contracts for independent model outputs.

These contracts preserve Gradient Boosting and Decision Tree results
separately. They do not execute inference, compare probabilities, or create
any combined probability.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from churn_app.domain.risk_level import RiskLevel


class ModelType(StrEnum):
    """Closed set of exported model identities."""

    GRADIENT_BOOSTING = "gradient_boosting"
    DECISION_TREE = "decision_tree"


class ModelRole(StrEnum):
    """Closed set of approved model roles."""

    PRIMARY = "primary"
    SENSITIVITY_COMPLEMENT = "sensitivity_complement"


@dataclass(frozen=True, slots=True)
class ModelIdentity:
    """Model identity and architectural role from the exported metadata."""

    model_type: ModelType
    role: ModelRole
    display_name: str


@dataclass(frozen=True, slots=True)
class ModelPrediction:
    """Prediction produced by one model pipeline.

    `probability` is model-specific and optional. It is not a confidence
    score and must not be combined with another model's probability.
    """

    model: ModelIdentity
    predicted_class: int
    probability: float | None = None


@dataclass(frozen=True, slots=True)
class OrchestrationResult:
    """Future consolidated decision-support result.

    The risk level is supplied by the future decision-policy implementation.
    This contract only preserves the shape of the output expected by later
    presentation code.
    """

    risk_level: RiskLevel
    gradient_boosting: ModelPrediction
    decision_tree: ModelPrediction
    interpretation: str | None = None
    recommendation: str | None = None
