"""Presentation-neutral interpretation contracts for churn risk analysis.

The contracts in this module describe deterministic explanatory content.
They do not contain recommendations, UI markup, colors, icons, or customer
actions.
"""

from __future__ import annotations

from dataclasses import dataclass

from churn_app.domain.risk_level import RiskLevel


@dataclass(frozen=True, slots=True)
class InterpretationResult:
    """Structured explanation of an already assigned churn risk level."""

    risk_level: RiskLevel
    title: str
    summary: str
    model_agreement: str
    evidence: tuple[str, ...]
    rationale: tuple[str, ...]
