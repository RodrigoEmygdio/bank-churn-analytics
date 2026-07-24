"""Unit tests for presentation-layer contract composition."""

from __future__ import annotations

from dataclasses import FrozenInstanceError, replace

import pytest

from churn_app.domain import (
    InterpretationResult,
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
    interpretation = _interpretation(RiskLevel.HIGH)
    recommendation = _recommendation(RiskLevel.HIGH)

    result = build_presentation(interpretation, recommendation)

    assert result == PresentationResult(
        risk_level=RiskLevel.HIGH,
        title=interpretation.title,
        summary=interpretation.summary,
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


def test_build_presentation_rejects_risk_mismatch() -> None:
    with pytest.raises(PresentationConsistencyError):
        build_presentation(
            _interpretation(RiskLevel.HIGH),
            _recommendation(RiskLevel.LOW),
        )


def test_presentation_result_is_immutable() -> None:
    result = build_presentation(
        _interpretation(RiskLevel.CRITICAL),
        _recommendation(RiskLevel.CRITICAL),
    )

    with pytest.raises(FrozenInstanceError):
        result.title = "Changed"  # type: ignore[misc]
    with pytest.raises(TypeError):
        result.evidence[0] = "Changed"  # type: ignore[index]
    with pytest.raises(TypeError):
        result.recommendations[0] = "Changed"  # type: ignore[index]


def test_build_presentation_is_deterministic() -> None:
    interpretation = _interpretation(RiskLevel.MODERATE)
    recommendation = _recommendation(RiskLevel.MODERATE)

    first = build_presentation(interpretation, recommendation)
    second = build_presentation(interpretation, recommendation)

    assert first == second


def test_build_presentation_does_not_mutate_inputs() -> None:
    interpretation = _interpretation(RiskLevel.HIGH)
    recommendation = _recommendation(RiskLevel.HIGH)
    original_interpretation = replace(interpretation)
    original_recommendation = replace(recommendation)

    build_presentation(interpretation, recommendation)

    assert interpretation == original_interpretation
    assert recommendation == original_recommendation


def test_build_presentation_rejects_wrong_interpretation_type() -> None:
    with pytest.raises(InvalidPresentationInputError):
        build_presentation(object(), _recommendation(RiskLevel.LOW))  # type: ignore[arg-type]


def test_build_presentation_rejects_wrong_recommendation_type() -> None:
    with pytest.raises(InvalidPresentationInputError):
        build_presentation(_interpretation(RiskLevel.LOW), object())  # type: ignore[arg-type]


def test_build_presentation_rejects_interpretation_with_string_risk_level() -> None:
    interpretation = _interpretation("HIGH")  # type: ignore[arg-type]

    with pytest.raises(InvalidPresentationInputError):
        build_presentation(interpretation, _recommendation(RiskLevel.HIGH))


def test_build_presentation_rejects_recommendation_with_string_risk_level() -> None:
    recommendation = _recommendation("HIGH")  # type: ignore[arg-type]

    with pytest.raises(InvalidPresentationInputError):
        build_presentation(_interpretation(RiskLevel.HIGH), recommendation)


def test_presentation_result_has_no_framework_fields() -> None:
    result = build_presentation(
        _interpretation(RiskLevel.LOW),
        _recommendation(RiskLevel.LOW),
    )

    assert not hasattr(result, "html")
    assert not hasattr(result, "markdown")
    assert not hasattr(result, "streamlit")
    assert not hasattr(result, "color")
    assert not hasattr(result, "icon")
    assert not hasattr(result, "css_class")


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
