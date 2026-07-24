"""Repository-controlled configuration for the churn application.

This module defines stable local paths only. It intentionally does not load
metadata, deserialize artifacts, import Streamlit, or read environment state.
"""

from __future__ import annotations

from pathlib import Path

PACKAGE_ROOT: Path = Path(__file__).resolve().parent
SRC_ROOT: Path = PACKAGE_ROOT.parent
REPOSITORY_ROOT: Path = SRC_ROOT.parent
ARTIFACTS_DIR: Path = REPOSITORY_ROOT / "artifacts"
METADATA_FILE: Path = ARTIFACTS_DIR / "metadata.json"
REFERENCE_PREDICTIONS_FILE: Path = ARTIFACTS_DIR / "reference_predictions.csv"
