"""Unit tests for the prediction-service inference boundary."""

from __future__ import annotations

import math

import numpy as np
import pandas as pd
import pytest

from churn_app.domain import (
    ModelIdentity,
    ModelPrediction,
    ModelRole,
    ModelType,
    PredictionResult,
)
from churn_app.services.artifact_loader import (
    LoadedArtifacts,
    load_metadata,
)
from churn_app.services.prediction_service import (
    InvalidPredictionValueError,
    ModelPredictionError,
    ProbabilityUnavailableError,
    UnexpectedPredictionShapeError,
    predict,
)


class PredictOnlyPipeline:
    """Minimal pipeline double exposing only class prediction."""

    def __init__(self, prediction: object) -> None:
        self.prediction = prediction

    def predict(self, model_input: pd.DataFrame) -> object:
        assert isinstance(model_input, pd.DataFrame)
        return self.prediction


class ProbabilityPipeline(PredictOnlyPipeline):
    """Minimal pipeline double exposing class prediction and probabilities."""

    def __init__(
        self,
        prediction: object,
        probabilities: object,
        classes: object = np.array([0, 1]),
    ) -> None:
        super().__init__(prediction)
        self.probabilities = probabilities
        self.classes_ = classes

    def predict_proba(self, model_input: pd.DataFrame) -> object:
        assert isinstance(model_input, pd.DataFrame)
        return self.probabilities


class NoPredictPipeline:
    """Pipeline double without the required predict method."""


def test_predict_executes_both_pipelines_independently() -> None:
    artifacts = _loaded_artifacts(
        gradient_boosting_pipeline=ProbabilityPipeline([1], [[0.2, 0.8]]),
        decision_tree_pipeline=ProbabilityPipeline([0], [[0.7, 0.3]]),
    )

    result = predict(artifacts, _model_input())

    assert isinstance(result, PredictionResult)
    assert result.gradient_boosting.model.model_type is ModelType.GRADIENT_BOOSTING
    assert result.gradient_boosting.model.role is ModelRole.PRIMARY
    assert result.gradient_boosting.predicted_class == 1
    assert result.gradient_boosting.probability == 0.8
    assert result.gradient_boosting.supports_probability is True
    assert result.decision_tree.model.model_type is ModelType.DECISION_TREE
    assert result.decision_tree.model.role is ModelRole.SENSITIVITY_COMPLEMENT
    assert result.decision_tree.predicted_class == 0
    assert result.decision_tree.probability == 0.3
    assert result.decision_tree.supports_probability is True


def test_predict_accepts_pipeline_without_predict_proba() -> None:
    artifacts = _loaded_artifacts(
        gradient_boosting_pipeline=PredictOnlyPipeline([0]),
        decision_tree_pipeline=PredictOnlyPipeline([1]),
    )

    result = predict(artifacts, _model_input())

    assert result.gradient_boosting.probability is None
    assert result.gradient_boosting.supports_probability is False
    assert result.decision_tree.probability is None
    assert result.decision_tree.supports_probability is False


@pytest.mark.parametrize("predicted_class", [0, 1, np.int64(0), np.int64(1)])
def test_predict_accepts_supported_prediction_classes(predicted_class: object) -> None:
    artifacts = _loaded_artifacts(
        gradient_boosting_pipeline=PredictOnlyPipeline([predicted_class]),
        decision_tree_pipeline=PredictOnlyPipeline([0]),
    )

    result = predict(artifacts, _model_input())

    assert result.gradient_boosting.predicted_class in {0, 1}


@pytest.mark.parametrize("prediction", [[2], [-1], [None], [True], [1.0]])
def test_predict_rejects_invalid_prediction_values(prediction: object) -> None:
    artifacts = _loaded_artifacts(
        gradient_boosting_pipeline=PredictOnlyPipeline(prediction),
        decision_tree_pipeline=PredictOnlyPipeline([0]),
    )

    with pytest.raises(InvalidPredictionValueError):
        predict(artifacts, _model_input())


@pytest.mark.parametrize(
    "prediction", [None, [], [0, 1], [[1]], [[0], [0, 1]], np.array([[0, 1]])]
)
def test_predict_rejects_unexpected_prediction_shapes(prediction: object) -> None:
    artifacts = _loaded_artifacts(
        gradient_boosting_pipeline=PredictOnlyPipeline(prediction),
        decision_tree_pipeline=PredictOnlyPipeline([0]),
    )

    expected_exception = (
        InvalidPredictionValueError
        if prediction is None
        else UnexpectedPredictionShapeError
    )
    with pytest.raises(expected_exception):
        predict(artifacts, _model_input())


def test_predict_rejects_pipeline_without_predict() -> None:
    artifacts = _loaded_artifacts(
        gradient_boosting_pipeline=NoPredictPipeline(),
        decision_tree_pipeline=PredictOnlyPipeline([0]),
    )

    with pytest.raises(ModelPredictionError):
        predict(artifacts, _model_input())


@pytest.mark.parametrize(
    "probabilities",
    [
        [[0.3, math.nan]],
        [[0.3, math.inf]],
        [[0.3, -0.1]],
        [[0.3, 1.1]],
        [[0.3, None]],
    ],
)
def test_predict_rejects_invalid_probability_values(probabilities: object) -> None:
    artifacts = _loaded_artifacts(
        gradient_boosting_pipeline=ProbabilityPipeline([1], probabilities),
        decision_tree_pipeline=PredictOnlyPipeline([0]),
    )

    with pytest.raises(InvalidPredictionValueError):
        predict(artifacts, _model_input())


@pytest.mark.parametrize(
    "probabilities",
    [None, [], [0.2, 0.8], [[0.2, 0.8], [0.3, 0.7]], [[0.2], [0.3, 0.7]]],
)
def test_predict_rejects_unexpected_probability_shapes(probabilities: object) -> None:
    artifacts = _loaded_artifacts(
        gradient_boosting_pipeline=ProbabilityPipeline([1], probabilities),
        decision_tree_pipeline=PredictOnlyPipeline([0]),
    )

    expected_exception = (
        InvalidPredictionValueError
        if probabilities is None
        else UnexpectedPredictionShapeError
    )
    with pytest.raises(expected_exception):
        predict(artifacts, _model_input())


def test_predict_rejects_missing_positive_class_probability() -> None:
    artifacts = _loaded_artifacts(
        gradient_boosting_pipeline=ProbabilityPipeline(
            [1], [[0.2, 0.8]], classes=np.array([0, 2])
        ),
        decision_tree_pipeline=PredictOnlyPipeline([0]),
    )

    with pytest.raises(ProbabilityUnavailableError):
        predict(artifacts, _model_input())


def test_predict_rejects_irregular_classes_shape() -> None:
    artifacts = _loaded_artifacts(
        gradient_boosting_pipeline=ProbabilityPipeline(
            [1], [[0.2, 0.8]], classes=[[0], [0, 1]]
        ),
        decision_tree_pipeline=PredictOnlyPipeline([0]),
    )

    with pytest.raises(UnexpectedPredictionShapeError):
        predict(artifacts, _model_input())


@pytest.mark.parametrize(
    ("classes", "probabilities"),
    [
        ([0, 1, 2], [[0.4, 0.6]]),
        ([0, 1], [[0.2, 0.3, 0.5]]),
    ],
)
def test_predict_rejects_class_probability_count_mismatch(
    classes: object, probabilities: object
) -> None:
    artifacts = _loaded_artifacts(
        gradient_boosting_pipeline=ProbabilityPipeline(
            [1], probabilities, classes=classes
        ),
        decision_tree_pipeline=PredictOnlyPipeline([0]),
    )

    with pytest.raises(UnexpectedPredictionShapeError, match="does not match classes_"):
        predict(artifacts, _model_input())


def test_prediction_result_exposes_no_dataframe_or_risk_level() -> None:
    artifacts = _loaded_artifacts(
        gradient_boosting_pipeline=ProbabilityPipeline([1], [[0.2, 0.8]]),
        decision_tree_pipeline=PredictOnlyPipeline([0]),
    )

    result = predict(artifacts, _model_input())

    assert not isinstance(result.gradient_boosting, pd.DataFrame)
    assert not isinstance(result.decision_tree, pd.DataFrame)
    assert not hasattr(result, "risk_level")
    assert not hasattr(result, "model_input")
    assert not hasattr(result, "combined_probability")
    assert not hasattr(result, "average_probability")
    assert not hasattr(result, "ensemble_probability")
    assert not hasattr(result, "confidence_score")


def test_probability_support_is_derived_from_probability_value() -> None:
    identity = ModelIdentity(
        model_type=ModelType.GRADIENT_BOOSTING,
        role=ModelRole.PRIMARY,
        display_name="Gradient Boosting",
    )

    with_probability = ModelPrediction(
        model=identity,
        predicted_class=1,
        probability=0.8,
    )
    without_probability = ModelPrediction(
        model=identity,
        predicted_class=0,
        probability=None,
    )

    assert with_probability.supports_probability is True
    assert without_probability.supports_probability is False
    with pytest.raises(TypeError):
        ModelPrediction(
            model=identity,
            predicted_class=1,
            probability=0.8,
            supports_probability=False,
        )


def _loaded_artifacts(
    gradient_boosting_pipeline: object,
    decision_tree_pipeline: object,
) -> LoadedArtifacts:
    metadata = load_metadata()
    return LoadedArtifacts(
        metadata=metadata,
        gradient_boosting_pipeline=gradient_boosting_pipeline,
        decision_tree_pipeline=decision_tree_pipeline,
    )


def _model_input() -> pd.DataFrame:
    return pd.DataFrame({"feature": [1]})
