"""Unit tests for presentation-layer contract composition."""

from __future__ import annotations

from dataclasses import FrozenInstanceError, replace

import pytest

from churn_app.domain import (
    InterpretationResult,
    ModelIdentity,
    ModelPrediction,
    ModelPresentationResult,
    ModelRole,
    ModelType,
    PredictionResult,
    PresentationResult,
    RecommendationPriority,
    RecommendationResult,
    RiskLevel,
)
from churn_app.services.presentation_layer import (
    InvalidPresentationInputError,
    PresentationConsistencyError,
    build_presentation,
)


def test_build_presentation_copies_every_field_exactly() -> None:
    prediction = _prediction()
    interpretation = _interpretation(RiskLevel.HIGH)
    recommendation = _recommendation(RiskLevel.HIGH)

    result = build_presentation(prediction, interpretation, recommendation)

    assert result == PresentationResult(
        risk_level=RiskLevel.HIGH,
        title=interpretation.title,
        summary=interpretation.summary,
        gradient_boosting=ModelPresentationResult(
            display_name="Gradient Boosting",
            predicted_class=1,
            predicted_label="Churn",
            churn_probability=0.617,
        ),
        decision_tree=ModelPresentationResult(
            display_name="Decision Tree",
            predicted_class=0,
            predicted_label="Retention",
            churn_probability=None,
        ),
        model_agreement=interpretation.model_agreement,
        evidence=interpretation.evidence,
        rationale=interpretation.rationale,
        recommendation_priority=recommendation.priority,
        objective=recommendation.objective,
        recommendations=recommendation.recommendations,
        expected_outcome=recommendation.expected_outcome,
    )
    assert result.evidence is interpretation.evidence
    assert result.rationale is interpretation.rationale
    assert result.recommendations is recommendation.recommendations
    assert result.gradient_boosting.churn_probability == 0.617
    assert result.decision_tree.churn_probability is None


def test_build_presentation_rejects_risk_mismatch() -> None:
    with pytest.raises(PresentationConsistencyError):
        build_presentation(
            _prediction(),
            _interpretation(RiskLevel.HIGH),
            _recommendation(RiskLevel.LOW),
        )


def test_presentation_result_is_immutable() -> None:
    result = build_presentation(
        _prediction(),
        _interpretation(RiskLevel.CRITICAL),
        _recommendation(RiskLevel.CRITICAL),
    )

    with pytest.raises(FrozenInstanceError):
        result.title = "Changed"  # type: ignore[misc]
    with pytest.raises(TypeError):
        result.evidence[0] = "Changed"  # type: ignore[index]
    with pytest.raises(TypeError):
        result.recommendations[0] = "Changed"  # type: ignore[index]


def test_model_presentation_result_is_immutable() -> None:
    model = ModelPresentationResult(
        display_name="Gradient Boosting",
        predicted_class=1,
        predicted_label="Churn",
        churn_probability=0.5,
    )

    with pytest.raises(FrozenInstanceError):
        model.predicted_label = "Retention"  # type: ignore[misc]


def test_build_presentation_is_deterministic() -> None:
    prediction = _prediction()
    interpretation = _interpretation(RiskLevel.MODERATE)
    recommendation = _recommendation(RiskLevel.MODERATE)

    first = build_presentation(prediction, interpretation, recommendation)
    second = build_presentation(prediction, interpretation, recommendation)

    assert first == second


def test_build_presentation_does_not_mutate_inputs() -> None:
    prediction = _prediction()
    interpretation = _interpretation(RiskLevel.HIGH)
    recommendation = _recommendation(RiskLevel.HIGH)
    original_prediction = replace(prediction)
    original_interpretation = replace(interpretation)
    original_recommendation = replace(recommendation)

    build_presentation(prediction, interpretation, recommendation)

    assert prediction == original_prediction
    assert interpretation == original_interpretation
    assert recommendation == original_recommendation


def test_build_presentation_requires_prediction_result() -> None:
    with pytest.raises(InvalidPresentationInputError):
        build_presentation(  # type: ignore[arg-type]
            object(),
            _interpretation(RiskLevel.LOW),
            _recommendation(RiskLevel.LOW),
        )


def test_build_presentation_rejects_wrong_interpretation_type() -> None:
    with pytest.raises(InvalidPresentationInputError):
        build_presentation(_prediction(), object(), _recommendation(RiskLevel.LOW))  # type: ignore[arg-type]


def test_build_presentation_rejects_wrong_recommendation_type() -> None:
    with pytest.raises(InvalidPresentationInputError):
        build_presentation(_prediction(), _interpretation(RiskLevel.LOW), object())  # type: ignore[arg-type]


def test_build_presentation_rejects_interpretation_with_string_risk_level() -> None:
    interpretation = _interpretation("HIGH")  # type: ignore[arg-type]

    with pytest.raises(InvalidPresentationInputError):
        build_presentation(
            _prediction(), interpretation, _recommendation(RiskLevel.HIGH)
        )


def test_build_presentation_rejects_recommendation_with_string_risk_level() -> None:
    recommendation = _recommendation("HIGH")  # type: ignore[arg-type]

    with pytest.raises(InvalidPresentationInputError):
        build_presentation(
            _prediction(), _interpretation(RiskLevel.HIGH), recommendation
        )


@pytest.mark.parametrize("predicted_class", [-1, 2, True, 1.0, "1", None])
def test_build_presentation_rejects_invalid_predicted_class(
    predicted_class: object,
) -> None:
    prediction = _prediction(
        gradient_boosting=ModelPrediction(
            model=_model_identity(ModelType.GRADIENT_BOOSTING, ModelRole.PRIMARY),
            predicted_class=predicted_class,  # type: ignore[arg-type]
            probability=0.5,
        )
    )

    with pytest.raises(InvalidPresentationInputError):
        build_presentation(
            prediction,
            _interpretation(RiskLevel.HIGH),
            _recommendation(RiskLevel.HIGH),
        )


@pytest.mark.parametrize("probability", [-0.1, 1.1, True, float("nan"), float("inf")])
def test_build_presentation_rejects_invalid_probability(probability: object) -> None:
    prediction = _prediction(
        gradient_boosting=ModelPrediction(
            model=_model_identity(ModelType.GRADIENT_BOOSTING, ModelRole.PRIMARY),
            predicted_class=1,
            probability=probability,  # type: ignore[arg-type]
        )
    )

    with pytest.raises(InvalidPresentationInputError):
        build_presentation(
            prediction,
            _interpretation(RiskLevel.HIGH),
            _recommendation(RiskLevel.HIGH),
        )


def test_presentation_result_has_no_framework_fields() -> None:
    result = build_presentation(
        _prediction(),
        _interpretation(RiskLevel.LOW),
        _recommendation(RiskLevel.LOW),
    )

    assert not hasattr(result, "html")
    assert not hasattr(result, "markdown")
    assert not hasattr(result, "streamlit")
    assert not hasattr(result, "color")
    assert not hasattr(result, "icon")
    assert not hasattr(result, "css_class")
    assert not hasattr(result, "combined_probability")
    assert not hasattr(result, "average_probability")
    assert not hasattr(result, "ensemble_probability")
    assert not hasattr(result, "confidence_score")


def _prediction(
    gradient_boosting: ModelPrediction | None = None,
    decision_tree: ModelPrediction | None = None,
) -> PredictionResult:
    return PredictionResult(
        gradient_boosting=gradient_boosting
        or ModelPrediction(
            model=_model_identity(ModelType.GRADIENT_BOOSTING, ModelRole.PRIMARY),
            predicted_class=1,
            probability=0.617,
        ),
        decision_tree=decision_tree
        or ModelPrediction(
            model=_model_identity(
                ModelType.DECISION_TREE,
                ModelRole.SENSITIVITY_COMPLEMENT,
            ),
            predicted_class=0,
            probability=None,
        ),
    )


def _model_identity(model_type: ModelType, role: ModelRole) -> ModelIdentity:
    return ModelIdentity(
        model_type=model_type,
        role=role,
        display_name={
            ModelType.GRADIENT_BOOSTING: "Gradient Boosting",
            ModelType.DECISION_TREE: "Decision Tree",
        }[model_type],
    )


def _interpretation(risk_level: RiskLevel) -> InterpretationResult:
    return InterpretationResult(
        risk_level=risk_level,
        title="High Churn Risk",
        summary="The primary prediction model detected evidence associated with customer churn.",
        model_agreement="Only the primary model predicted churn.",
        evidence=(
            "Gradient Boosting predicted churn.",
            "Decision Tree predicted retention.",
        ),
        rationale=(
            "The primary model detected churn.",
            "The complementary model did not confirm the prediction.",
            "This disagreement corresponds to high churn risk.",
        ),
    )


def _recommendation(risk_level: RiskLevel) -> RecommendationResult:
    return RecommendationResult(
        risk_level=risk_level,
        priority=RecommendationPriority.HIGH,
        objective="Reduce customer churn risk through proactive engagement.",
        recommendations=(
            "Contact the customer.",
            "Review customer satisfaction.",
            "Evaluate appropriate retention actions.",
        ),
        expected_outcome="Customer retention opportunities are identified before churn occurs.",
    )
