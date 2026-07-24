"""Unit tests for the approved four-level decision policy."""

from __future__ import annotations

from dataclasses import replace

import pytest

from churn_app.domain import (
    ModelIdentity,
    ModelPrediction,
    ModelRole,
    ModelType,
    PredictionResult,
    RiskLevel,
)
from churn_app.services.decision_policy import (
    InvalidDecisionInputError,
    determine_risk_level,
)


@pytest.fixture
def gradient_boosting_identity() -> ModelIdentity:
    return ModelIdentity(
        model_type=ModelType.GRADIENT_BOOSTING,
        role=ModelRole.PRIMARY,
        display_name="Gradient Boosting",
    )


@pytest.fixture
def decision_tree_identity() -> ModelIdentity:
    return ModelIdentity(
        model_type=ModelType.DECISION_TREE,
        role=ModelRole.SENSITIVITY_COMPLEMENT,
        display_name="Decision Tree",
    )


@pytest.mark.parametrize(
    ("gb_class", "dt_class", "expected_risk"),
    [
        (0, 0, RiskLevel.LOW),
        (0, 1, RiskLevel.MODERATE),
        (1, 0, RiskLevel.HIGH),
        (1, 1, RiskLevel.CRITICAL),
    ],
)
def test_determine_risk_level_applies_complete_decision_table(
    gb_class: int,
    dt_class: int,
    expected_risk: RiskLevel,
    gradient_boosting_identity: ModelIdentity,
    decision_tree_identity: ModelIdentity,
) -> None:
    prediction_result = _prediction_result(
        gradient_boosting_identity=gradient_boosting_identity,
        decision_tree_identity=decision_tree_identity,
        gb_class=gb_class,
        dt_class=dt_class,
    )

    risk_level = determine_risk_level(prediction_result)

    assert risk_level is expected_risk
    assert isinstance(risk_level, RiskLevel)
    assert type(risk_level) is RiskLevel
    assert not isinstance(risk_level, int)


@pytest.mark.parametrize(
    ("gb_class", "gb_probability", "dt_class", "dt_probability", "expected_risk"),
    [
        (1, 0.51, 0, 0.99, RiskLevel.HIGH),
        (0, 0.01, 1, 0.51, RiskLevel.MODERATE),
        (1, None, 1, None, RiskLevel.CRITICAL),
        (0, None, 0, 0.99, RiskLevel.LOW),
    ],
)
def test_determine_risk_level_ignores_probabilities(
    gb_class: int,
    gb_probability: float | None,
    dt_class: int,
    dt_probability: float | None,
    expected_risk: RiskLevel,
    gradient_boosting_identity: ModelIdentity,
    decision_tree_identity: ModelIdentity,
) -> None:
    prediction_result = _prediction_result(
        gradient_boosting_identity=gradient_boosting_identity,
        decision_tree_identity=decision_tree_identity,
        gb_class=gb_class,
        dt_class=dt_class,
        gb_probability=gb_probability,
        dt_probability=dt_probability,
    )

    assert determine_risk_level(prediction_result) is expected_risk


@pytest.mark.parametrize("invalid_class", [-1, 2, None, True, False, 1.0, "1"])
def test_determine_risk_level_rejects_invalid_gradient_boosting_class(
    invalid_class: object,
    gradient_boosting_identity: ModelIdentity,
    decision_tree_identity: ModelIdentity,
) -> None:
    prediction_result = _prediction_result(
        gradient_boosting_identity=gradient_boosting_identity,
        decision_tree_identity=decision_tree_identity,
        gb_class=invalid_class,
        dt_class=0,
    )

    with pytest.raises(
        InvalidDecisionInputError, match="invalid predicted class for gradient_boosting"
    ):
        determine_risk_level(prediction_result)


@pytest.mark.parametrize("invalid_class", [-1, 2, None, True, False, 1.0, "1"])
def test_determine_risk_level_rejects_invalid_decision_tree_class(
    invalid_class: object,
    gradient_boosting_identity: ModelIdentity,
    decision_tree_identity: ModelIdentity,
) -> None:
    prediction_result = _prediction_result(
        gradient_boosting_identity=gradient_boosting_identity,
        decision_tree_identity=decision_tree_identity,
        gb_class=0,
        dt_class=invalid_class,
    )

    with pytest.raises(
        InvalidDecisionInputError, match="invalid predicted class for decision_tree"
    ):
        determine_risk_level(prediction_result)


def test_determine_risk_level_does_not_mutate_prediction_result(
    gradient_boosting_identity: ModelIdentity,
    decision_tree_identity: ModelIdentity,
) -> None:
    prediction_result = _prediction_result(
        gradient_boosting_identity=gradient_boosting_identity,
        decision_tree_identity=decision_tree_identity,
        gb_class=1,
        dt_class=0,
        gb_probability=0.51,
        dt_probability=0.99,
    )
    original_gradient_boosting = replace(prediction_result.gradient_boosting)
    original_decision_tree = replace(prediction_result.decision_tree)

    assert determine_risk_level(prediction_result) is RiskLevel.HIGH

    assert prediction_result.gradient_boosting == original_gradient_boosting
    assert prediction_result.decision_tree == original_decision_tree
    assert prediction_result.gradient_boosting.probability == 0.51
    assert prediction_result.decision_tree.probability == 0.99
    assert prediction_result.gradient_boosting.model == gradient_boosting_identity
    assert prediction_result.decision_tree.model == decision_tree_identity


def _prediction_result(
    *,
    gradient_boosting_identity: ModelIdentity,
    decision_tree_identity: ModelIdentity,
    gb_class: object,
    dt_class: object,
    gb_probability: float | None = 0.75,
    dt_probability: float | None = 0.25,
) -> PredictionResult:
    return PredictionResult(
        gradient_boosting=ModelPrediction(
            model=gradient_boosting_identity,
            predicted_class=gb_class,  # type: ignore[arg-type]
            probability=gb_probability,
        ),
        decision_tree=ModelPrediction(
            model=decision_tree_identity,
            predicted_class=dt_class,  # type: ignore[arg-type]
            probability=dt_probability,
        ),
    )
