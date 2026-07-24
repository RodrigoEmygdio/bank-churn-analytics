"""Prediction service boundary.

Future stages will execute both complete exported pipelines and preserve their
model-specific outputs independently. This module must not determine risk
levels.
"""

from __future__ import annotations

from typing import Any

from churn_app.domain import ModelPrediction


def predict_with_model(
    model: object, input_data: object, model_metadata: dict[str, Any]
) -> ModelPrediction:
    """Execute a single model pipeline in a future implementation stage.

    TODO(Prompt 5): Implement pipeline prediction and probability extraction.
    """
    raise NotImplementedError("Model prediction is deferred to Prompt 5.")


def predict_with_both_models(
    models: object, input_data: object, metadata: dict[str, Any]
) -> tuple[ModelPrediction, ModelPrediction]:
    """Execute both exported pipelines in a future implementation stage.

    TODO(Prompt 5): Preserve Gradient Boosting and Decision Tree outputs
    independently.
    """
    raise NotImplementedError("Dual-model prediction is deferred to Prompt 5.")
