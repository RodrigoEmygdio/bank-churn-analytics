"""Trusted local artifact loading for the churn application.

This module owns metadata parsing, repository integrity validation, hash
verification, and joblib deserialization. It intentionally performs no file
I/O at import time.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any

import joblib

from churn_app import config

SUPPORTED_ARTIFACT_VERSION = "1.0.0"
REQUIRED_MODELS = ("gradient_boosting", "decision_tree")
EXPECTED_DECISION_POLICY = MappingProxyType(
    {
        "gb_0_dt_0": "low",
        "gb_0_dt_1": "attention",
        "gb_1_dt_0": "high",
        "gb_1_dt_1": "critical",
    }
)


class ArtifactError(Exception):
    """Base exception for deterministic artifact-management failures."""


class MetadataError(ArtifactError):
    """Raised when metadata cannot be read or parsed."""


class MetadataSchemaError(MetadataError):
    """Raised when metadata content does not match the required schema."""


class MissingArtifactError(ArtifactError):
    """Raised when a required repository-controlled file is missing."""


class HashMismatchError(ArtifactError):
    """Raised when an artifact hash differs from metadata."""


class UnsupportedMetadataVersionError(MetadataError):
    """Raised when metadata declares an unsupported artifact version."""


class ArtifactLoadError(ArtifactError):
    """Raised when a validated artifact cannot be deserialized."""


@dataclass(frozen=True, slots=True)
class ModelArtifactMetadata:
    """Validated metadata for one exported model artifact."""

    name: str
    file: str
    role: str
    sha256: str
    metrics: Mapping[str, float]


@dataclass(frozen=True, slots=True)
class InputSchemaMetadata:
    """Validated model input schema declared by metadata."""

    feature_names: tuple[str, ...]
    feature_count: int
    dtypes: Mapping[str, str]


@dataclass(frozen=True, slots=True)
class ArtifactMetadata:
    """Validated repository metadata contract."""

    project: str
    artifact_version: str
    exported_at_utc: str
    python_version: str
    scikit_learn_version: str
    pandas_version: str
    numpy_version: str
    joblib_version: str
    target: str
    positive_class: int
    models: Mapping[str, ModelArtifactMetadata]
    decision_policy: Mapping[str, str]
    input_schema: InputSchemaMetadata


@dataclass(frozen=True, slots=True)
class LoadedArtifacts:
    """Validated metadata and trusted local model pipelines."""

    metadata: ArtifactMetadata
    gradient_boosting_pipeline: object
    decision_tree_pipeline: object


def load_metadata(metadata_file: Path = config.METADATA_FILE) -> ArtifactMetadata:
    """Load and validate repository metadata from JSON."""
    if not metadata_file.is_file():
        raise MissingArtifactError(f"Metadata file not found: {metadata_file}")

    try:
        raw_metadata = json.loads(metadata_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise MetadataError(
            f"Metadata file is not valid JSON: {metadata_file}"
        ) from exc

    return _parse_metadata(raw_metadata)


def load_model_artifacts(artifacts_dir: Path = config.ARTIFACTS_DIR) -> LoadedArtifacts:
    """Validate the repository artifact set and load trusted local pipelines."""
    metadata_file = artifacts_dir / "metadata.json"
    reference_predictions_file = artifacts_dir / "reference_predictions.csv"

    metadata = load_metadata(metadata_file)
    validate_repository_files(metadata, artifacts_dir, reference_predictions_file)
    validate_artifact_hashes(metadata, artifacts_dir)

    return LoadedArtifacts(
        metadata=metadata,
        gradient_boosting_pipeline=_load_pipeline(
            artifacts_dir / metadata.models["gradient_boosting"].file
        ),
        decision_tree_pipeline=_load_pipeline(
            artifacts_dir / metadata.models["decision_tree"].file
        ),
    )


def validate_repository_files(
    metadata: ArtifactMetadata,
    artifacts_dir: Path = config.ARTIFACTS_DIR,
    reference_predictions_file: Path = config.REFERENCE_PREDICTIONS_FILE,
) -> None:
    """Verify that metadata, reference predictions, and declared artifacts exist."""
    if not (artifacts_dir / "metadata.json").is_file():
        raise MissingArtifactError(f"Metadata file not found in: {artifacts_dir}")

    if not reference_predictions_file.is_file():
        raise MissingArtifactError(
            f"Reference predictions file not found: {reference_predictions_file}"
        )

    for model in metadata.models.values():
        artifact_file = artifacts_dir / model.file
        if not artifact_file.is_file():
            raise MissingArtifactError(f"Model artifact not found: {artifact_file}")


def validate_artifact_hashes(
    metadata: ArtifactMetadata, artifacts_dir: Path = config.ARTIFACTS_DIR
) -> None:
    """Compare declared artifact hashes against local file content."""
    for model in metadata.models.values():
        artifact_file = artifacts_dir / model.file
        actual_hash = calculate_sha256(artifact_file)
        if actual_hash != model.sha256:
            raise HashMismatchError(
                f"SHA-256 mismatch for {artifact_file.name}: "
                f"expected {model.sha256}, got {actual_hash}"
            )


def calculate_sha256(path: Path) -> str:
    """Calculate SHA-256 for a local repository artifact."""
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_pipeline(path: Path) -> object:
    try:
        return joblib.load(path)
    except Exception as exc:
        raise ArtifactLoadError(f"Could not load artifact: {path}") from exc


def _parse_metadata(raw_metadata: Any) -> ArtifactMetadata:
    if not isinstance(raw_metadata, dict):
        raise MetadataSchemaError("Metadata root must be a JSON object.")

    _require_keys(
        raw_metadata,
        {
            "project",
            "artifact_version",
            "exported_at_utc",
            "python_version",
            "scikit_learn_version",
            "pandas_version",
            "numpy_version",
            "joblib_version",
            "target",
            "positive_class",
            "models",
            "decision_policy",
            "input_schema",
        },
        "metadata",
    )

    artifact_version = _require_str(raw_metadata, "artifact_version", "metadata")
    if artifact_version != SUPPORTED_ARTIFACT_VERSION:
        raise UnsupportedMetadataVersionError(
            f"Unsupported artifact metadata version: {artifact_version}"
        )

    decision_policy = _parse_decision_policy(raw_metadata["decision_policy"])
    input_schema = _parse_input_schema(raw_metadata["input_schema"])
    models = _parse_models(raw_metadata["models"])

    return ArtifactMetadata(
        project=_require_str(raw_metadata, "project", "metadata"),
        artifact_version=artifact_version,
        exported_at_utc=_require_str(raw_metadata, "exported_at_utc", "metadata"),
        python_version=_require_str(raw_metadata, "python_version", "metadata"),
        scikit_learn_version=_require_str(
            raw_metadata, "scikit_learn_version", "metadata"
        ),
        pandas_version=_require_str(raw_metadata, "pandas_version", "metadata"),
        numpy_version=_require_str(raw_metadata, "numpy_version", "metadata"),
        joblib_version=_require_str(raw_metadata, "joblib_version", "metadata"),
        target=_require_str(raw_metadata, "target", "metadata"),
        positive_class=_require_int(raw_metadata, "positive_class", "metadata"),
        models=models,
        decision_policy=decision_policy,
        input_schema=input_schema,
    )


def _parse_models(raw_models: Any) -> Mapping[str, ModelArtifactMetadata]:
    if not isinstance(raw_models, dict):
        raise MetadataSchemaError("metadata.models must be an object.")

    missing_models = set(REQUIRED_MODELS) - raw_models.keys()
    if missing_models:
        raise MetadataSchemaError(
            f"metadata.models missing required entries: {sorted(missing_models)}"
        )

    parsed_models: dict[str, ModelArtifactMetadata] = {}
    for model_name in REQUIRED_MODELS:
        model_data = raw_models[model_name]
        if not isinstance(model_data, dict):
            raise MetadataSchemaError(
                f"metadata.models.{model_name} must be an object."
            )

        _require_keys(model_data, {"file", "role", "sha256"}, f"model {model_name}")
        metrics = {
            key: float(value)
            for key, value in model_data.items()
            if key.startswith("test_") and isinstance(value, int | float)
        }
        parsed_models[model_name] = ModelArtifactMetadata(
            name=model_name,
            file=_require_str(model_data, "file", f"model {model_name}"),
            role=_require_str(model_data, "role", f"model {model_name}"),
            sha256=_require_sha256(model_data, f"model {model_name}"),
            metrics=MappingProxyType(metrics),
        )

    return MappingProxyType(parsed_models)


def _parse_input_schema(raw_input_schema: Any) -> InputSchemaMetadata:
    if not isinstance(raw_input_schema, dict):
        raise MetadataSchemaError("metadata.input_schema must be an object.")

    _require_keys(
        raw_input_schema,
        {"feature_names", "feature_count", "dtypes"},
        "input_schema",
    )
    raw_feature_names = raw_input_schema["feature_names"]
    if not isinstance(raw_feature_names, list) or not all(
        isinstance(feature, str) for feature in raw_feature_names
    ):
        raise MetadataSchemaError(
            "input_schema.feature_names must be a list of strings."
        )

    feature_count = _require_int(raw_input_schema, "feature_count", "input_schema")
    feature_names = tuple(raw_feature_names)
    if feature_count != len(feature_names):
        raise MetadataSchemaError(
            "input_schema.feature_count must match the number of feature names."
        )

    raw_dtypes = raw_input_schema["dtypes"]
    if not isinstance(raw_dtypes, dict) or not all(
        isinstance(key, str) and isinstance(value, str)
        for key, value in raw_dtypes.items()
    ):
        raise MetadataSchemaError("input_schema.dtypes must map strings to strings.")

    missing_dtypes = set(feature_names) - raw_dtypes.keys()
    unexpected_dtypes = raw_dtypes.keys() - set(feature_names)
    if missing_dtypes or unexpected_dtypes:
        raise MetadataSchemaError(
            "input_schema.dtypes must match feature_names exactly: "
            f"missing={sorted(missing_dtypes)}, unexpected={sorted(unexpected_dtypes)}"
        )

    return InputSchemaMetadata(
        feature_names=feature_names,
        feature_count=feature_count,
        dtypes=MappingProxyType(dict(raw_dtypes)),
    )


def _parse_decision_policy(raw_decision_policy: Any) -> Mapping[str, str]:
    if not isinstance(raw_decision_policy, dict):
        raise MetadataSchemaError("metadata.decision_policy must be an object.")

    if raw_decision_policy != EXPECTED_DECISION_POLICY:
        raise MetadataSchemaError("metadata.decision_policy does not match AGENTS.md.")

    return MappingProxyType(dict(raw_decision_policy))


def _require_keys(data: Mapping[str, Any], keys: set[str], context: str) -> None:
    missing = keys - data.keys()
    if missing:
        raise MetadataSchemaError(f"{context} missing required keys: {sorted(missing)}")


def _require_str(data: Mapping[str, Any], key: str, context: str) -> str:
    value = data[key]
    if not isinstance(value, str) or not value:
        raise MetadataSchemaError(f"{context}.{key} must be a non-empty string.")
    return value


def _require_int(data: Mapping[str, Any], key: str, context: str) -> int:
    value = data[key]
    if not isinstance(value, int) or isinstance(value, bool):
        raise MetadataSchemaError(f"{context}.{key} must be an integer.")
    return value


def _require_sha256(data: Mapping[str, Any], context: str) -> str:
    value = _require_str(data, "sha256", context)
    if len(value) != 64 or any(
        character not in "0123456789abcdef" for character in value
    ):
        raise MetadataSchemaError(f"{context}.sha256 must be a lowercase SHA-256 hash.")
    return value
