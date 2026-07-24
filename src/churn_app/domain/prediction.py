"""Prediction domain contracts for independent model outputs.

These contracts preserve Gradient Boosting and Decision Tree results
separately. They do not execute inference, compare probabilities, or create
any combined probability.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


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

    @property
    def supports_probability(self) -> bool:
        """Whether this model exposed a model-specific probability."""
        return self.probability is not None


@dataclass(frozen=True, slots=True)
class PredictionResult:
    """Independent outputs produced by the two exported pipelines.

    This contract contains no risk level, recommendation, interpretation, or
    combined probability.
    """

    gradient_boosting: ModelPrediction
    decision_tree: ModelPrediction
