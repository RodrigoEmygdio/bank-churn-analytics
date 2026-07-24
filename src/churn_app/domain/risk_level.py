"""Closed risk-level domain for the approved four-level policy.

The enum declares valid risk levels only. It intentionally does not implement
the mapping from model predictions to risk levels.
"""

from __future__ import annotations

from enum import StrEnum


class RiskLevel(StrEnum):
    """Approved consolidated risk levels."""

    LOW = "LOW"
    ATTENTION = "ATTENTION"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
