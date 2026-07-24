"""Execution boundary for trusted exported model pipelines.

This module runs already-loaded pipelines against an already validated,
model-ready DataFrame. It does not load artifacts, build input features,
determine risk levels, interpret predictions, or render UI.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from typing import Any

import numpy as np
import pandas as pd

from churn_app.domain import (
    ModelIdentity,
    ModelPrediction,
    ModelRole,
    ModelType,
    PredictionResult,
)
from churn_app.services.artifact_loader import LoadedArtifacts, ModelArtifactMetadata


class PredictionError(Exception):
    """Base exception for deterministic prediction-service failures."""


class ModelPredictionError(PredictionError):
    """Raised when a model prediction operation fails."""

    def __init__(self, model_name: str, operation: str, message: str) -> None:
        self.model_name = model_name
        self.operation = operation
        super().__init__(f"{model_name} {operation} failed: {message}")


class UnexpectedPredictionShapeError(ModelPredictionError):
    """Raised when model output does not contain exactly one usable result."""


class InvalidPredictionValueError(ModelPredictionError):
    """Raised when model output contains unsupported classes or probabilities."""


class ProbabilityUnavailableError(ModelPredictionError):
    """Raised when positive-class probability cannot be located."""


def predict(
    artifacts: LoadedArtifacts,
    model_input: pd.DataFrame,
) -> PredictionResult:
    """Execute both exported pipelines and return independent model outputs."""
    metadata = artifacts.metadata
    return PredictionResult(
        gradient_boosting=predict_with_model(
            pipeline=artifacts.gradient_boosting_pipeline,
            model_input=model_input,
            model_metadata=metadata.models["gradient_boosting"],
            model_type=ModelType.GRADIENT_BOOSTING,
            positive_class=metadata.positive_class,
        ),
        decision_tree=predict_with_model(
            pipeline=artifacts.decision_tree_pipeline,
            model_input=model_input,
            model_metadata=metadata.models["decision_tree"],
            model_type=ModelType.DECISION_TREE,
            positive_class=metadata.positive_class,
        ),
    )


def predict_with_model(
    pipeline: object,
    model_input: pd.DataFrame,
    model_metadata: ModelArtifactMetadata,
    model_type: ModelType,
    positive_class: int,
) -> ModelPrediction:
    """Execute one pipeline and normalize its class and probability output."""
    model_identity = _build_model_identity(model_metadata, model_type)
    predicted_class = _predict_class(pipeline, model_metadata.name, model_input)
    probability = _predict_positive_probability(
        pipeline=pipeline,
        model_name=model_metadata.name,
        model_input=model_input,
        positive_class=positive_class,
    )
    return ModelPrediction(
        model=model_identity,
        predicted_class=predicted_class,
        probability=probability,
    )


def _build_model_identity(
    model_metadata: ModelArtifactMetadata, model_type: ModelType
) -> ModelIdentity:
    role = _parse_model_role(model_metadata)
    display_name = {
        ModelType.GRADIENT_BOOSTING: "Gradient Boosting",
        ModelType.DECISION_TREE: "Decision Tree",
    }[model_type]
    return ModelIdentity(
        model_type=model_type,
        role=role,
        display_name=display_name,
    )


def _parse_model_role(model_metadata: ModelArtifactMetadata) -> ModelRole:
    try:
        return ModelRole(model_metadata.role)
    except ValueError as exc:
        raise InvalidPredictionValueError(
            model_metadata.name,
            "metadata role parsing",
            f"unsupported role {model_metadata.role!r}",
        ) from exc


def _predict_class(pipeline: object, model_name: str, model_input: pd.DataFrame) -> int:
    predict_method = getattr(pipeline, "predict", None)
    if not callable(predict_method):
        raise ModelPredictionError(model_name, "predict", "pipeline has no predict")

    try:
        raw_prediction = predict_method(model_input)
    except Exception as exc:
        raise ModelPredictionError(
            model_name, "predict", "pipeline raised an exception"
        ) from exc

    prediction_value = _extract_single_value(
        raw_prediction,
        model_name=model_name,
        operation="predict",
    )
    return _validate_predicted_class(prediction_value, model_name)


def _predict_positive_probability(
    pipeline: object,
    model_name: str,
    model_input: pd.DataFrame,
    positive_class: int,
) -> float | None:
    predict_proba_method = getattr(pipeline, "predict_proba", None)
    if not callable(predict_proba_method):
        return None

    try:
        raw_probabilities = predict_proba_method(model_input)
    except Exception as exc:
        raise ModelPredictionError(
            model_name, "predict_proba", "pipeline raised an exception"
        ) from exc

    probabilities = _validate_probability_shape(raw_probabilities, model_name)
    positive_class_index = _positive_class_index(
        pipeline=pipeline,
        model_name=model_name,
        positive_class=positive_class,
        probability_count=probabilities.shape[1],
    )
    probability = probabilities[0, positive_class_index]
    return _validate_probability_value(probability, model_name)


def _extract_single_value(output: object, model_name: str, operation: str) -> object:
    if output is None:
        raise InvalidPredictionValueError(
            model_name, operation, "output must not be None"
        )

    values = _as_array(output, model_name=model_name, operation=operation)
    if values.ndim != 1 or values.shape[0] != 1:
        raise UnexpectedPredictionShapeError(
            model_name,
            operation,
            f"expected one-dimensional output with one value, got shape {values.shape}",
        )
    return values[0]


def _validate_predicted_class(value: object, model_name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int | np.integer):
        raise InvalidPredictionValueError(
            model_name,
            "predict",
            f"predicted class must be integer 0 or 1, got {value!r}",
        )

    predicted_class = int(value)
    if predicted_class not in {0, 1}:
        raise InvalidPredictionValueError(
            model_name,
            "predict",
            f"predicted class must be 0 or 1, got {predicted_class!r}",
        )
    return predicted_class


def _validate_probability_shape(output: object, model_name: str) -> np.ndarray:
    if output is None:
        raise InvalidPredictionValueError(
            model_name, "predict_proba", "output must not be None"
        )

    probabilities = _as_array(output, model_name=model_name, operation="predict_proba")
    if probabilities.ndim != 2 or probabilities.shape[0] != 1:
        raise UnexpectedPredictionShapeError(
            model_name,
            "predict_proba",
            "expected two-dimensional output with one row, "
            f"got shape {probabilities.shape}",
        )
    if probabilities.shape[1] < 1:
        raise UnexpectedPredictionShapeError(
            model_name,
            "predict_proba",
            f"expected at least one class probability, got shape {probabilities.shape}",
        )
    return probabilities


def _positive_class_index(
    pipeline: object,
    model_name: str,
    positive_class: int,
    probability_count: int,
) -> int:
    raw_classes = getattr(pipeline, "classes_", None)
    if raw_classes is None:
        raise ProbabilityUnavailableError(
            model_name,
            "predict_proba",
            "pipeline does not expose classes_ for positive-class lookup",
        )

    classes = _as_one_dimensional_sequence(raw_classes, model_name)
    if len(classes) != probability_count:
        raise UnexpectedPredictionShapeError(
            model_name,
            "predict_proba",
            "probability column count does not match classes_",
        )

    matches = [index for index, value in enumerate(classes) if value == positive_class]
    if not matches:
        raise ProbabilityUnavailableError(
            model_name,
            "predict_proba",
            f"positive class {positive_class!r} is absent from classes_",
        )

    positive_index = matches[0]
    if positive_index >= probability_count:
        raise UnexpectedPredictionShapeError(
            model_name,
            "predict_proba",
            "probability output has fewer columns than classes_ requires",
        )
    return positive_index


def _as_one_dimensional_sequence(value: object, model_name: str) -> Sequence[Any]:
    classes = _as_array(value, model_name=model_name, operation="classes_")
    if classes.ndim != 1 or classes.shape[0] == 0:
        raise UnexpectedPredictionShapeError(
            model_name,
            "classes_",
            f"expected one-dimensional non-empty classes_, got shape {classes.shape}",
        )
    return classes.tolist()


def _as_array(output: object, *, model_name: str, operation: str) -> np.ndarray:
    try:
        return np.asarray(output)
    except (TypeError, ValueError) as exc:
        raise UnexpectedPredictionShapeError(
            model_name,
            operation,
            "output could not be converted to a regular array",
        ) from exc


def _validate_probability_value(value: object, model_name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, int | float | np.number):
        raise InvalidPredictionValueError(
            model_name,
            "predict_proba",
            f"probability must be numeric, got {value!r}",
        )

    probability = float(value)
    if not math.isfinite(probability):
        raise InvalidPredictionValueError(
            model_name, "predict_proba", "probability must be finite"
        )
    if not 0.0 <= probability <= 1.0:
        raise InvalidPredictionValueError(
            model_name,
            "predict_proba",
            f"probability must be in [0, 1], got {probability!r}",
        )
    return probability
