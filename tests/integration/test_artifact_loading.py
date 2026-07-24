"""Integration tests for repository-controlled artifact loading."""

from __future__ import annotations

from churn_app.services.artifact_loader import LoadedArtifacts, load_model_artifacts


def test_repository_artifacts_load_successfully() -> None:
    loaded = load_model_artifacts()

    assert isinstance(loaded, LoadedArtifacts)
    assert hasattr(loaded.gradient_boosting_pipeline, "predict")
    assert hasattr(loaded.decision_tree_pipeline, "predict")
