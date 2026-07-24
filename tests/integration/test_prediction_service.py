"""Integration tests for executing repository-controlled prediction artifacts."""

from __future__ import annotations

from churn_app.domain import CustomerInput, PredictionResult
from churn_app.services.artifact_loader import load_model_artifacts
from churn_app.services.input_builder import build_model_input
from churn_app.services.prediction_service import predict


def test_prediction_service_executes_both_exported_pipelines() -> None:
    artifacts = load_model_artifacts()
    model_input = build_model_input(
        CustomerInput(
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
        ),
        artifacts.metadata,
    )

    result = predict(artifacts, model_input)

    assert isinstance(result, PredictionResult)
    assert result.gradient_boosting.predicted_class in {0, 1}
    assert result.decision_tree.predicted_class in {0, 1}
    assert result.gradient_boosting.probability is not None
    assert result.decision_tree.probability is not None
    assert 0.0 <= result.gradient_boosting.probability <= 1.0
    assert 0.0 <= result.decision_tree.probability <= 1.0
    assert not hasattr(result, "risk_level")
    assert not hasattr(result, "combined_probability")
