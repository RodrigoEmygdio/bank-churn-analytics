"""Result rendering boundary for the Streamlit application.

This module renders only fields already present in `PresentationResult`. It
does not create business wording, apply policy, or generate recommendations.
"""

from __future__ import annotations

from collections.abc import Iterable

import streamlit as st

from churn_app.domain import PresentationResult


def render_result(result: PresentationResult) -> None:
    """Render a presentation-ready churn-risk result."""
    if type(result) is not PresentationResult:
        raise TypeError("result must be a PresentationResult.")

    st.header(result.title)
    st.write(result.summary)

    st.subheader("Risk Level")
    st.write(result.risk_level.value)

    st.subheader("Model Agreement")
    st.write(result.model_agreement)

    st.subheader("Evidence")
    _render_items(result.evidence)

    st.subheader("Business Rationale")
    _render_items(result.rationale)

    st.subheader("Recommendation Priority")
    st.write(result.recommendation_priority.value)

    st.subheader("Objective")
    st.write(result.objective)

    st.subheader("Recommendations")
    _render_items(result.recommendations)

    st.subheader("Expected Outcome")
    st.write(result.expected_outcome)


def _render_items(items: Iterable[str]) -> None:
    for item in items:
        st.markdown(f"- {item}")
