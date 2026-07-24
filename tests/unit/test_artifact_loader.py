"""Unit tests for metadata validation and trusted artifact loading."""

from __future__ import annotations

import json
from dataclasses import FrozenInstanceError
from pathlib import Path
from typing import Any

import pytest

from churn_app.services import artifact_loader
from churn_app.services.artifact_loader import (
    ArtifactMetadata,
    HashMismatchError,
    LoadedArtifacts,
    MetadataError,
    MetadataSchemaError,
    MissingArtifactError,
    UnsupportedMetadataVersionError,
)


def test_load_metadata_success() -> None:
    metadata = artifact_loader.load_metadata(Path("artifacts/metadata.json"))

    assert isinstance(metadata, ArtifactMetadata)
    assert metadata.artifact_version == "1.0.0"
    assert metadata.positive_class == 1
    assert metadata.models["gradient_boosting"].role == "primary"
    assert metadata.models["decision_tree"].role == "sensitivity_complement"
    assert metadata.input_schema.feature_count == len(
        metadata.input_schema.feature_names
    )


def test_load_metadata_rejects_invalid_json(tmp_path: Path) -> None:
    metadata_file = tmp_path / "metadata.json"
    metadata_file.write_text("{not-json", encoding="utf-8")

    with pytest.raises(MetadataError):
        artifact_loader.load_metadata(metadata_file)


def test_load_metadata_rejects_missing_metadata(tmp_path: Path) -> None:
    with pytest.raises(MissingArtifactError):
        artifact_loader.load_metadata(tmp_path / "metadata.json")


def test_load_metadata_rejects_unsupported_version(tmp_path: Path) -> None:
    metadata = _valid_metadata()
    metadata["artifact_version"] = "2.0.0"
    metadata_file = _write_metadata(tmp_path, metadata)

    with pytest.raises(UnsupportedMetadataVersionError):
        artifact_loader.load_metadata(metadata_file)


def test_load_metadata_rejects_invalid_schema(tmp_path: Path) -> None:
    metadata = _valid_metadata()
    metadata.pop("input_schema")
    metadata_file = _write_metadata(tmp_path, metadata)

    with pytest.raises(MetadataSchemaError):
        artifact_loader.load_metadata(metadata_file)


def test_load_metadata_rejects_missing_hash_section(tmp_path: Path) -> None:
    metadata = _valid_metadata()
    metadata["models"]["gradient_boosting"].pop("sha256")
    metadata_file = _write_metadata(tmp_path, metadata)

    with pytest.raises(MetadataSchemaError):
        artifact_loader.load_metadata(metadata_file)


def test_load_model_artifacts_rejects_missing_reference_predictions(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write_valid_repository(tmp_path, include_reference_predictions=False)
    _fail_if_joblib_load_is_called(monkeypatch)

    with pytest.raises(MissingArtifactError):
        artifact_loader.load_model_artifacts(tmp_path)


def test_load_model_artifacts_rejects_missing_declared_artifact(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write_valid_repository(tmp_path, include_decision_tree=False)
    _fail_if_joblib_load_is_called(monkeypatch)

    with pytest.raises(MissingArtifactError):
        artifact_loader.load_model_artifacts(tmp_path)


def test_load_model_artifacts_rejects_hash_mismatch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write_valid_repository(tmp_path)
    metadata = _valid_metadata(tmp_path)
    metadata["models"]["gradient_boosting"]["sha256"] = "0" * 64
    _write_metadata(tmp_path, metadata)
    _fail_if_joblib_load_is_called(monkeypatch)

    with pytest.raises(HashMismatchError):
        artifact_loader.load_model_artifacts(tmp_path)


def test_load_model_artifacts_success_returns_loaded_artifacts(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write_valid_repository(tmp_path)
    loaded_paths: list[Path] = []

    def fake_joblib_load(path: Path) -> object:
        loaded_paths.append(path)
        return {"loaded": path.name}

    monkeypatch.setattr(artifact_loader.joblib, "load", fake_joblib_load)

    loaded = artifact_loader.load_model_artifacts(tmp_path)

    assert isinstance(loaded, LoadedArtifacts)
    assert loaded.metadata.artifact_version == "1.0.0"
    assert loaded.gradient_boosting_pipeline == {
        "loaded": "gradient_boosting_pipeline.joblib"
    }
    assert loaded.decision_tree_pipeline == {"loaded": "decision_tree_pipeline.joblib"}
    assert [path.name for path in loaded_paths] == [
        "gradient_boosting_pipeline.joblib",
        "decision_tree_pipeline.joblib",
    ]


def test_loaded_artifacts_contract_is_immutable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write_valid_repository(tmp_path)
    monkeypatch.setattr(artifact_loader.joblib, "load", lambda path: object())

    loaded = artifact_loader.load_model_artifacts(tmp_path)

    with pytest.raises(FrozenInstanceError):
        loaded.metadata = loaded.metadata


def _fail_if_joblib_load_is_called(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail(path: Path) -> object:
        raise AssertionError(f"joblib.load should not have been called for {path}")

    monkeypatch.setattr(artifact_loader.joblib, "load", fail)


def _write_valid_repository(
    artifacts_dir: Path,
    *,
    include_reference_predictions: bool = True,
    include_decision_tree: bool = True,
) -> None:
    (artifacts_dir / "gradient_boosting_pipeline.joblib").write_bytes(b"gb-artifact")
    if include_decision_tree:
        (artifacts_dir / "decision_tree_pipeline.joblib").write_bytes(b"dt-artifact")
    if include_reference_predictions:
        (artifacts_dir / "reference_predictions.csv").write_text(
            "source_index,CreditScore\n1,650\n", encoding="utf-8"
        )
    _write_metadata(artifacts_dir, _valid_metadata(artifacts_dir))


def _write_metadata(artifacts_dir: Path, metadata: dict[str, Any]) -> Path:
    metadata_file = artifacts_dir / "metadata.json"
    metadata_file.write_text(json.dumps(metadata), encoding="utf-8")
    return metadata_file


def _valid_metadata(artifacts_dir: Path | None = None) -> dict[str, Any]:
    gb_hash = "a" * 64
    dt_hash = "b" * 64
    if artifacts_dir is not None:
        gb_hash = artifact_loader.calculate_sha256(
            artifacts_dir / "gradient_boosting_pipeline.joblib"
        )
        dt_path = artifacts_dir / "decision_tree_pipeline.joblib"
        if dt_path.exists():
            dt_hash = artifact_loader.calculate_sha256(dt_path)

    return {
        "project": "bank-customer-churn",
        "artifact_version": "1.0.0",
        "exported_at_utc": "2026-07-24T07:52:44.689492+00:00",
        "python_version": "3.14.3",
        "scikit_learn_version": "1.9.0",
        "pandas_version": "3.0.3",
        "numpy_version": "2.5.1",
        "joblib_version": "1.5.3",
        "target": "Exited",
        "positive_class": 1,
        "models": {
            "gradient_boosting": {
                "file": "gradient_boosting_pipeline.joblib",
                "role": "primary",
                "test_accuracy": 0.87,
                "sha256": gb_hash,
            },
            "decision_tree": {
                "file": "decision_tree_pipeline.joblib",
                "role": "sensitivity_complement",
                "test_accuracy": 0.7795,
                "sha256": dt_hash,
            },
        },
        "decision_policy": {
            "gb_0_dt_0": "low",
            "gb_0_dt_1": "attention",
            "gb_1_dt_0": "high",
            "gb_1_dt_1": "critical",
        },
        "input_schema": {
            "feature_names": [
                "CreditScore",
                "Geography",
                "Gender",
                "Age",
                "Tenure",
                "Balance",
                "NumOfProducts",
                "HasCrCard",
                "IsActiveMember",
                "EstimatedSalary",
                "ProductsGroup",
            ],
            "feature_count": 11,
            "dtypes": {
                "CreditScore": "int64",
                "Geography": "str",
                "Gender": "str",
                "Age": "int64",
                "Tenure": "int64",
                "Balance": "float64",
                "NumOfProducts": "int64",
                "HasCrCard": "int64",
                "IsActiveMember": "int64",
                "EstimatedSalary": "float64",
                "ProductsGroup": "category",
            },
        },
    }
