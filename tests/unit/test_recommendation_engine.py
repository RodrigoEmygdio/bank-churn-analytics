"""Unit tests for deterministic recommendation generation."""

from __future__ import annotations

from dataclasses import FrozenInstanceError, replace

import pytest

from churn_app.domain import (
    InterpretationResult,
    RecommendationPriority,
    RecommendationResult,
    RiskLevel,
)
from churn_app.services.recommendation_engine import (
    InvalidRecommendationInputError,
    generate_recommendation,
)

RECOMMENDATION_CASES = [
    (
        RiskLevel.LOW,
        RecommendationPriority.LOW,
        "Maintain customer relationship.",
        (
            "Continue periodic monitoring.",
            "Maintain current customer engagement.",
            "No immediate retention action is required.",
        ),
        "Customer relationship remains stable through normal monitoring.",
    ),
    (
        RiskLevel.MODERATE,
        RecommendationPriority.MEDIUM,
        "Investigate potential early churn indicators.",
        (
            "Review recent customer activity.",
            "Monitor account behavior.",
            "Consider proactive customer contact if additional indicators emerge.",
        ),
        "Potential churn indicators are assessed before escalation.",
    ),
    (
        RiskLevel.HIGH,
        RecommendationPriority.HIGH,
        "Reduce customer churn risk through proactive engagement.",
        (
            "Contact the customer.",
            "Review customer satisfaction.",
            "Evaluate appropriate retention actions.",
        ),
        "Customer retention opportunities are identified before churn occurs.",
    ),
    (
        RiskLevel.CRITICAL,
        RecommendationPriority.URGENT,
        "Execute immediate customer retention strategy.",
        (
            "Initiate urgent retention campaign.",
            "Escalate to customer success team.",
            "Prioritize executive follow-up if applicable.",
        ),
        "Immediate intervention maximizes retention opportunity.",
    ),
]


@pytest.mark.parametrize(
    (
        "risk_level",
        "priority",
        "objective",
        "recommendations",
        "expected_outcome",
    ),
    RECOMMENDATION_CASES,
)
def test_generate_recommendation_returns_exact_contract(
    risk_level: RiskLevel,
    priority: RecommendationPriority,
    objective: str,
    recommendations: tuple[str, ...],
    expected_outcome: str,
) -> None:
    result = generate_recommendation(_interpretation(risk_level))

    assert result == RecommendationResult(
        risk_level=risk_level,
        priority=priority,
        objective=objective,
        recommendations=recommendations,
        expected_outcome=expected_outcome,
    )


def test_generate_recommendation_is_deterministic() -> None:
    interpretation = _interpretation(RiskLevel.HIGH)

    first = generate_recommendation(interpretation)
    second = generate_recommendation(interpretation)

    assert first == second


def test_generate_recommendation_uses_only_risk_level() -> None:
    first = generate_recommendation(
        InterpretationResult(
            risk_level=RiskLevel.MODERATE,
            title="A",
            summary="A",
            model_agreement="A",
            evidence=("Different evidence.",),
            rationale=("Different rationale.",),
        )
    )
    second = generate_recommendation(
        InterpretationResult(
            risk_level=RiskLevel.MODERATE,
            title="B",
            summary="B",
            model_agreement="B",
            evidence=("Other evidence.",),
            rationale=("Other rationale.",),
        )
    )

    assert first == second


def test_recommendation_result_is_immutable() -> None:
    result = generate_recommendation(_interpretation(RiskLevel.CRITICAL))

    with pytest.raises(FrozenInstanceError):
        result.objective = "Changed"  # type: ignore[misc]
    with pytest.raises(TypeError):
        result.recommendations[0] = "Changed"  # type: ignore[index]


def test_generate_recommendation_does_not_mutate_input() -> None:
    interpretation = _interpretation(RiskLevel.HIGH)
    original = replace(interpretation)

    generate_recommendation(interpretation)

    assert interpretation == original


def test_generate_recommendation_rejects_wrong_input_type() -> None:
    with pytest.raises(InvalidRecommendationInputError):
        generate_recommendation(object())  # type: ignore[arg-type]


def test_generate_recommendation_rejects_invalid_risk_level() -> None:
    interpretation = InterpretationResult(
        risk_level="HIGH",  # type: ignore[arg-type]
        title="High Churn Risk",
        summary="Summary",
        model_agreement="Agreement",
        evidence=("Evidence.",),
        rationale=("Rationale.",),
    )

    with pytest.raises(InvalidRecommendationInputError):
        generate_recommendation(interpretation)


def test_recommendation_result_has_no_presentation_fields() -> None:
    result = generate_recommendation(_interpretation(RiskLevel.LOW))

    assert not hasattr(result, "html")
    assert not hasattr(result, "markdown")
    assert not hasattr(result, "color")
    assert not hasattr(result, "icon")
    assert not hasattr(result, "css_class")


def _interpretation(risk_level: RiskLevel) -> InterpretationResult:
    return InterpretationResult(
        risk_level=risk_level,
        title="Title",
        summary="Summary",
        model_agreement="Agreement",
        evidence=("Evidence.",),
        rationale=("Rationale.",),
    )
