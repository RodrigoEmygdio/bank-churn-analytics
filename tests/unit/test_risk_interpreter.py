"""Unit tests for deterministic risk interpretation."""

from __future__ import annotations

from dataclasses import FrozenInstanceError, replace

import pytest

from churn_app.domain import (
    InterpretationResult,
    ModelIdentity,
    ModelPrediction,
    ModelRole,
    ModelType,
    PredictionResult,
    RiskLevel,
)
from churn_app.services.risk_interpreter import (
    InterpretationConsistencyError,
    InvalidInterpretationInputError,
    interpret_risk,
)

INTERPRETATION_CASES = [
    (
        0,
        0,
        RiskLevel.LOW,
        "Low Churn Risk",
        "No consistent indication of customer churn was detected.",
        "Both models predicted customer retention.",
        (
            "Gradient Boosting predicted retention.",
            "Decision Tree predicted retention.",
        ),
        (
            "Neither model detected churn.",
            "The models agree on customer retention.",
            "The evidence does not indicate elevated churn risk.",
        ),
    ),
    (
        0,
        1,
        RiskLevel.MODERATE,
        "Moderate Churn Risk",
        "The complementary model detected a churn signal that was not confirmed by the primary model.",
        "Only the complementary model predicted churn.",
        (
            "Gradient Boosting predicted retention.",
            "Decision Tree predicted churn.",
        ),
        (
            "The primary model remained negative.",
            "The complementary model detected churn.",
            "This disagreement corresponds to moderate churn risk.",
        ),
    ),
    (
        1,
        0,
        RiskLevel.HIGH,
        "High Churn Risk",
        "The primary prediction model detected evidence associated with customer churn.",
        "Only the primary model predicted churn.",
        (
            "Gradient Boosting predicted churn.",
            "Decision Tree predicted retention.",
        ),
        (
            "The primary model detected churn.",
            "The complementary model did not confirm the prediction.",
            "This disagreement corresponds to high churn risk.",
        ),
    ),
    (
        1,
        1,
        RiskLevel.CRITICAL,
        "Critical Churn Risk",
        "Independent predictive models consistently detected customer churn indicators.",
        "Both models independently predicted churn.",
        (
            "Gradient Boosting predicted churn.",
            "Decision Tree predicted churn.",
        ),
        (
            "Both models detected churn.",
            "The evidence is mutually reinforcing.",
            "This agreement corresponds to critical churn risk.",
        ),
    ),
]


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
    (
        "gb_class",
        "dt_class",
        "risk_level",
        "title",
        "summary",
        "model_agreement",
        "evidence",
        "rationale",
    ),
    INTERPRETATION_CASES,
)
def test_interpret_risk_returns_exact_interpretation(
    gb_class: int,
    dt_class: int,
    risk_level: RiskLevel,
    title: str,
    summary: str,
    model_agreement: str,
    evidence: tuple[str, ...],
    rationale: tuple[str, ...],
    gradient_boosting_identity: ModelIdentity,
    decision_tree_identity: ModelIdentity,
) -> None:
    prediction_result = _prediction_result(
        gradient_boosting_identity=gradient_boosting_identity,
        decision_tree_identity=decision_tree_identity,
        gb_class=gb_class,
        dt_class=dt_class,
    )

    result = interpret_risk(prediction_result, risk_level)

    assert result == InterpretationResult(
        risk_level=risk_level,
        title=title,
        summary=summary,
        model_agreement=model_agreement,
        evidence=evidence,
        rationale=rationale,
    )


@pytest.mark.parametrize(
    ("gb_class", "dt_class", "valid_risk_level"),
    [(case[0], case[1], case[2]) for case in INTERPRETATION_CASES],
)
@pytest.mark.parametrize("supplied_risk_level", list(RiskLevel))
def test_interpret_risk_rejects_all_inconsistent_pairings(
    gb_class: int,
    dt_class: int,
    valid_risk_level: RiskLevel,
    supplied_risk_level: RiskLevel,
    gradient_boosting_identity: ModelIdentity,
    decision_tree_identity: ModelIdentity,
) -> None:
    prediction_result = _prediction_result(
        gradient_boosting_identity=gradient_boosting_identity,
        decision_tree_identity=decision_tree_identity,
        gb_class=gb_class,
        dt_class=dt_class,
    )

    if supplied_risk_level is valid_risk_level:
        assert interpret_risk(prediction_result, supplied_risk_level).risk_level is (
            valid_risk_level
        )
    else:
        with pytest.raises(InterpretationConsistencyError):
            interpret_risk(prediction_result, supplied_risk_level)


def test_interpret_risk_is_deterministic(
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

    first = interpret_risk(prediction_result, RiskLevel.HIGH)
    second = interpret_risk(prediction_result, RiskLevel.HIGH)

    assert first == second


def test_interpret_risk_does_not_use_probabilities(
    gradient_boosting_identity: ModelIdentity,
    decision_tree_identity: ModelIdentity,
) -> None:
    low_probabilities = _prediction_result(
        gradient_boosting_identity=gradient_boosting_identity,
        decision_tree_identity=decision_tree_identity,
        gb_class=0,
        dt_class=1,
        gb_probability=0.01,
        dt_probability=0.51,
    )
    high_probabilities = _prediction_result(
        gradient_boosting_identity=gradient_boosting_identity,
        decision_tree_identity=decision_tree_identity,
        gb_class=0,
        dt_class=1,
        gb_probability=0.99,
        dt_probability=0.99,
    )

    first = interpret_risk(low_probabilities, RiskLevel.MODERATE)
    second = interpret_risk(high_probabilities, RiskLevel.MODERATE)

    assert first == second
    assert all("0." not in text for text in first.evidence)
    assert all("probability" not in text.lower() for text in first.evidence)
    assert all("probability" not in text.lower() for text in first.rationale)


def test_interpretation_result_is_immutable(
    gradient_boosting_identity: ModelIdentity,
    decision_tree_identity: ModelIdentity,
) -> None:
    result = interpret_risk(
        _prediction_result(
            gradient_boosting_identity=gradient_boosting_identity,
            decision_tree_identity=decision_tree_identity,
            gb_class=1,
            dt_class=1,
        ),
        RiskLevel.CRITICAL,
    )

    with pytest.raises(FrozenInstanceError):
        result.title = "Changed"  # type: ignore[misc]
    with pytest.raises(TypeError):
        result.evidence[0] = "Changed"  # type: ignore[index]
    with pytest.raises(TypeError):
        result.rationale[0] = "Changed"  # type: ignore[index]


def test_interpret_risk_does_not_mutate_inputs(
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

    interpret_risk(prediction_result, RiskLevel.HIGH)

    assert prediction_result.gradient_boosting == original_gradient_boosting
    assert prediction_result.decision_tree == original_decision_tree


def test_interpret_risk_rejects_wrong_prediction_result_type() -> None:
    with pytest.raises(InvalidInterpretationInputError):
        interpret_risk(object(), RiskLevel.LOW)  # type: ignore[arg-type]


def test_interpret_risk_rejects_wrong_risk_level_type(
    gradient_boosting_identity: ModelIdentity,
    decision_tree_identity: ModelIdentity,
) -> None:
    prediction_result = _prediction_result(
        gradient_boosting_identity=gradient_boosting_identity,
        decision_tree_identity=decision_tree_identity,
        gb_class=0,
        dt_class=0,
    )

    with pytest.raises(InvalidInterpretationInputError):
        interpret_risk(prediction_result, "LOW")  # type: ignore[arg-type]


def test_interpret_risk_rejects_malformed_prediction_entries(
    decision_tree_identity: ModelIdentity,
) -> None:
    prediction_result = PredictionResult(
        gradient_boosting=object(),  # type: ignore[arg-type]
        decision_tree=ModelPrediction(
            model=decision_tree_identity,
            predicted_class=0,
        ),
    )

    with pytest.raises(InvalidInterpretationInputError):
        interpret_risk(prediction_result, RiskLevel.LOW)


def test_interpret_risk_rejects_swapped_model_identities(
    gradient_boosting_identity: ModelIdentity,
    decision_tree_identity: ModelIdentity,
) -> None:
    prediction_result = PredictionResult(
        gradient_boosting=ModelPrediction(
            model=decision_tree_identity,
            predicted_class=0,
        ),
        decision_tree=ModelPrediction(
            model=gradient_boosting_identity,
            predicted_class=0,
        ),
    )

    with pytest.raises(InvalidInterpretationInputError):
        interpret_risk(prediction_result, RiskLevel.LOW)


def test_interpret_risk_rejects_incorrect_gradient_boosting_model_type(
    decision_tree_identity: ModelIdentity,
) -> None:
    prediction_result = PredictionResult(
        gradient_boosting=ModelPrediction(
            model=decision_tree_identity,
            predicted_class=0,
        ),
        decision_tree=ModelPrediction(
            model=decision_tree_identity,
            predicted_class=0,
        ),
    )

    with pytest.raises(InvalidInterpretationInputError, match="gradient_boosting"):
        interpret_risk(prediction_result, RiskLevel.LOW)


def test_interpret_risk_rejects_incorrect_gradient_boosting_role(
    decision_tree_identity: ModelIdentity,
) -> None:
    gradient_boosting_with_wrong_role = ModelIdentity(
        model_type=ModelType.GRADIENT_BOOSTING,
        role=ModelRole.SENSITIVITY_COMPLEMENT,
        display_name="Gradient Boosting",
    )
    prediction_result = PredictionResult(
        gradient_boosting=ModelPrediction(
            model=gradient_boosting_with_wrong_role,
            predicted_class=0,
        ),
        decision_tree=ModelPrediction(
            model=decision_tree_identity,
            predicted_class=0,
        ),
    )

    with pytest.raises(InvalidInterpretationInputError, match="gradient_boosting"):
        interpret_risk(prediction_result, RiskLevel.LOW)


def test_interpret_risk_rejects_incorrect_decision_tree_model_type(
    gradient_boosting_identity: ModelIdentity,
) -> None:
    prediction_result = PredictionResult(
        gradient_boosting=ModelPrediction(
            model=gradient_boosting_identity,
            predicted_class=0,
        ),
        decision_tree=ModelPrediction(
            model=gradient_boosting_identity,
            predicted_class=0,
        ),
    )

    with pytest.raises(InvalidInterpretationInputError, match="decision_tree"):
        interpret_risk(prediction_result, RiskLevel.LOW)


def test_interpret_risk_rejects_incorrect_decision_tree_role(
    gradient_boosting_identity: ModelIdentity,
) -> None:
    decision_tree_with_wrong_role = ModelIdentity(
        model_type=ModelType.DECISION_TREE,
        role=ModelRole.PRIMARY,
        display_name="Decision Tree",
    )
    prediction_result = PredictionResult(
        gradient_boosting=ModelPrediction(
            model=gradient_boosting_identity,
            predicted_class=0,
        ),
        decision_tree=ModelPrediction(
            model=decision_tree_with_wrong_role,
            predicted_class=0,
        ),
    )

    with pytest.raises(InvalidInterpretationInputError, match="decision_tree"):
        interpret_risk(prediction_result, RiskLevel.LOW)


@pytest.mark.parametrize("invalid_class", [-1, 2, None, True, False, 1.0, "1"])
def test_interpret_risk_rejects_invalid_gradient_boosting_class(
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

    with pytest.raises(InvalidInterpretationInputError):
        interpret_risk(prediction_result, RiskLevel.LOW)


@pytest.mark.parametrize("invalid_class", [-1, 2, None, True, False, 1.0, "1"])
def test_interpret_risk_rejects_invalid_decision_tree_class(
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

    with pytest.raises(InvalidInterpretationInputError):
        interpret_risk(prediction_result, RiskLevel.LOW)


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
