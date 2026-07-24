"""Result rendering boundary for the Streamlit application.

This module renders only fields already present in `PresentationResult`. It
does not create business wording, apply policy, or generate recommendations.
"""

from __future__ import annotations

from collections.abc import Iterable

import streamlit as st

from churn_app.domain import ModelPresentationResult, PresentationResult, RiskLevel


def render_result(result: PresentationResult) -> None:
    """Render a presentation-ready churn-risk result."""
    if type(result) is not PresentationResult:
        raise TypeError("result must be a PresentationResult.")

    with st.container(border=True):
        st.subheader("Analysis Result")
        st.write(result.title)
        _render_risk_status(result)
        st.write(result.summary)

        metric_columns = st.columns(2)
        with metric_columns[0]:
            st.metric("Risk Level", result.risk_level.value)
        with metric_columns[1]:
            st.metric(
                "Recommendation Priority",
                result.recommendation_priority.value,
            )

        st.write("Objective")
        st.write(result.objective)

    with st.container(border=True):
        st.subheader("Model Predictions")
        model_columns = st.columns(2)
        with model_columns[0]:
            _render_model_result(result.gradient_boosting)
        with model_columns[1]:
            _render_model_result(result.decision_tree)

        st.write("Model Agreement")
        st.write(result.model_agreement)

    with st.container(border=True):
        st.subheader("Recommended Actions")
        st.write("Objective")
        st.write(result.objective)
        _render_items(result.recommendations)
        st.write("Expected Outcome")
        st.write(result.expected_outcome)

    with st.expander("Analysis Details", expanded=False):
        st.write("Evidence")
        _render_items(result.evidence)
        st.write("Business Rationale")
        _render_items(result.rationale)

    with st.expander("How this analysis is produced", expanded=False):
        st.write(
            "Customer Input -> Model Predictions -> Risk Decision -> "
            "Interpretation -> Recommendation"
        )


def _render_risk_status(result: PresentationResult) -> None:
    message = f"Risk Level: {result.risk_level.value}"
    if result.risk_level is RiskLevel.LOW:
        st.success(message)
    elif result.risk_level is RiskLevel.MODERATE:
        st.info(message)
    elif result.risk_level is RiskLevel.HIGH:
        st.warning(message)
    else:
        st.error(message)


def _render_model_result(model: ModelPresentationResult) -> None:
    with st.container(border=True):
        st.write(model.display_name)
        st.metric("Prediction", model.predicted_label)
        st.caption(f"Class: {model.predicted_class}")
        if model.churn_probability is None:
            st.write("Churn probability: Probability unavailable")
            return

        percentage = model.churn_probability * 100
        st.write(f"Churn probability: {percentage:.1f}%")
        st.progress(round(percentage))


def _render_items(items: Iterable[str]) -> None:
    items = tuple(items)
    if not items:
        st.write("No items available.")
        return
    st.markdown("\n".join(f"- {item}" for item in items))
