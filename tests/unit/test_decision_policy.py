"""Unit tests for the approved four-level decision policy."""

from __future__ import annotations

import pytest

from churn_app.domain import (
    ModelIdentity,
    ModelPrediction,
    ModelRole,
    ModelType,
    RiskLevel,
)
from churn_app.services.decision_policy import determine_risk_level


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
        (0, 1, RiskLevel.ATTENTION),
        (1, 0, RiskLevel.HIGH),
        (1, 1, RiskLevel.CRITICAL),
    ],
)
def test_determine_risk_level(
    gb_class: int,
    dt_class: int,
    expected_risk: RiskLevel,
    gradient_boosting_identity: ModelIdentity,
    decision_tree_identity: ModelIdentity,
) -> None:
    gb_prediction = ModelPrediction(
        model=gradient_boosting_identity,
        predicted_class=gb_class,
        probability=0.75,
    )
    dt_prediction = ModelPrediction(
        model=decision_tree_identity,
        predicted_class=dt_class,
        probability=0.25,
    )

    assert determine_risk_level(gb_prediction, dt_prediction) is expected_risk
