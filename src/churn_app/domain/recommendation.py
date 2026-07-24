"""Presentation-neutral recommendation contracts for churn risk analysis.

These contracts describe deterministic business recommendations. They do not
contain UI formatting, customer messages, colors, icons, or generated content.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from churn_app.domain.risk_level import RiskLevel


class RecommendationPriority(StrEnum):
    """Closed set of recommendation priorities."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"


@dataclass(frozen=True, slots=True)
class RecommendationResult:
    """Structured business recommendation for an interpreted risk level."""

    risk_level: RiskLevel
    priority: RecommendationPriority
    objective: str
    recommendations: tuple[str, ...]
    expected_outcome: str
