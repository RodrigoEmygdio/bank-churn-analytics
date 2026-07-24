"""Structural tests for the architecture materialization scaffold."""

from __future__ import annotations

import importlib

from churn_app import config, domain
from churn_app.domain import (
    CustomerInput,
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


def test_configuration_paths_resolve_to_repository_artifacts() -> None:
    assert config.REPOSITORY_ROOT.name == "bank-churn-analytics"
    assert config.ARTIFACTS_DIR == config.REPOSITORY_ROOT / "artifacts"
    assert config.METADATA_FILE == config.ARTIFACTS_DIR / "metadata.json"
    assert (
        config.REFERENCE_PREDICTIONS_FILE
        == config.ARTIFACTS_DIR / "reference_predictions.csv"
    )


def test_customer_input_excludes_derived_products_group() -> None:
    customer = CustomerInput(
        credit_score=650,
        geography="France",
        gender="Female",
        age=40,
        tenure=3,
        balance=1200.0,
        num_of_products=2,
        has_cr_card=1,
        is_active_member=1,
        estimated_salary=90000.0,
    )

    assert customer.num_of_products == 2
    assert not hasattr(customer, "products_group")


def test_risk_levels_are_exactly_approved_values() -> None:
    assert [level.value for level in RiskLevel] == [
        "LOW",
        "MODERATE",
        "HIGH",
        "CRITICAL",
    ]


def test_model_predictions_preserve_independent_probabilities() -> None:
    gb_identity = ModelIdentity(
        model_type=ModelType.GRADIENT_BOOSTING,
        role=ModelRole.PRIMARY,
        display_name="Gradient Boosting",
    )
    dt_identity = ModelIdentity(
        model_type=ModelType.DECISION_TREE,
        role=ModelRole.SENSITIVITY_COMPLEMENT,
        display_name="Decision Tree",
    )
    gb_prediction = ModelPrediction(
        model=gb_identity, predicted_class=1, probability=0.6
    )
    dt_prediction = ModelPrediction(
        model=dt_identity, predicted_class=0, probability=None
    )
    result = PredictionResult(
        gradient_boosting=gb_prediction,
        decision_tree=dt_prediction,
    )

    assert result.gradient_boosting.probability == 0.6
    assert result.gradient_boosting.supports_probability is True
    assert result.decision_tree.probability is None
    assert result.decision_tree.supports_probability is False
    assert not hasattr(result, "risk_level")
    assert not hasattr(result, "combined_probability")
    assert not hasattr(result, "average_probability")
    assert not hasattr(result, "ensemble_probability")
    assert not hasattr(result, "confidence_score")


def test_interpretation_result_separates_evidence_and_rationale() -> None:
    interpretation = InterpretationResult(
        risk_level=RiskLevel.HIGH,
        title="High Churn Risk",
        summary="Summary",
        model_agreement="Only the primary model predicted churn.",
        evidence=("Gradient Boosting predicted churn.",),
        rationale=("This disagreement corresponds to high churn risk.",),
    )

    assert interpretation.evidence == ("Gradient Boosting predicted churn.",)
    assert interpretation.rationale == (
        "This disagreement corresponds to high churn risk.",
    )
    assert not hasattr(interpretation, "recommendation")
    assert not hasattr(interpretation, "color")
    assert not hasattr(interpretation, "icon")


def test_recommendation_result_is_presentation_neutral() -> None:
    recommendation = RecommendationResult(
        risk_level=RiskLevel.MODERATE,
        priority=RecommendationPriority.MEDIUM,
        objective="Investigate potential early churn indicators.",
        recommendations=("Review recent customer activity.",),
        expected_outcome="Potential churn indicators are assessed before escalation.",
    )

    assert recommendation.priority is RecommendationPriority.MEDIUM
    assert recommendation.recommendations == ("Review recent customer activity.",)
    assert not hasattr(recommendation, "html")
    assert not hasattr(recommendation, "markdown")
    assert not hasattr(recommendation, "color")
    assert not hasattr(recommendation, "icon")


def test_presentation_result_aggregates_business_outputs_without_formatting() -> None:
    presentation = PresentationResult(
        risk_level=RiskLevel.HIGH,
        title="High Churn Risk",
        summary="Summary",
        gradient_boosting=ModelPresentationResult(
            display_name="Gradient Boosting",
            predicted_class=1,
            predicted_label="Churn",
            churn_probability=0.6,
        ),
        decision_tree=ModelPresentationResult(
            display_name="Decision Tree",
            predicted_class=0,
            predicted_label="Retention",
            churn_probability=None,
        ),
        model_agreement="Only the primary model predicted churn.",
        evidence=("Gradient Boosting predicted churn.",),
        rationale=("This disagreement corresponds to high churn risk.",),
        recommendation_priority=RecommendationPriority.HIGH,
        objective="Reduce customer churn risk through proactive engagement.",
        recommendations=("Contact the customer.",),
        expected_outcome="Customer retention opportunities are identified before churn occurs.",
    )

    assert presentation.recommendation_priority is RecommendationPriority.HIGH
    assert presentation.gradient_boosting.predicted_label == "Churn"
    assert presentation.decision_tree.churn_probability is None
    assert presentation.recommendations == ("Contact the customer.",)
    assert not hasattr(presentation, "html")
    assert not hasattr(presentation, "markdown")
    assert not hasattr(presentation, "color")
    assert not hasattr(presentation, "icon")


def test_domain_does_not_export_premature_orchestration_result() -> None:
    assert "OrchestrationResult" not in domain.__all__
    assert not hasattr(domain, "OrchestrationResult")


def test_boundary_modules_import_without_loading_artifacts() -> None:
    modules = [
        "churn_app",
        "churn_app.config",
        "churn_app.domain",
        "churn_app.services.artifact_loader",
        "churn_app.services.input_builder",
        "churn_app.services.prediction_service",
        "churn_app.services.risk_interpreter",
        "churn_app.services.recommendation_engine",
        "churn_app.services.presentation_layer",
        "churn_app.services.decision_policy",
        "churn_app.ui.form",
        "churn_app.ui.result",
    ]

    for module_name in modules:
        importlib.import_module(module_name)
