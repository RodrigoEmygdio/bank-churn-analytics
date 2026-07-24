"""Result rendering boundary for the Streamlit application.

This module renders only fields already present in `PresentationResult`. It
does not create business wording, apply policy, or generate recommendations.
"""

from __future__ import annotations

from collections.abc import Iterable

import streamlit as st

from churn_app.domain import ModelPresentationResult, PresentationResult, RiskLevel
from churn_app.i18n import (
    Locale,
    translate,
    translate_canonical_text,
    translate_format,
    translate_prediction_label,
    translate_priority,
    translate_risk_level,
)


def render_result(result: PresentationResult, locale: Locale) -> None:
    """Render a presentation-ready churn-risk result."""
    if type(result) is not PresentationResult:
        raise TypeError("result must be a PresentationResult.")

    with st.container(border=True):
        st.subheader(translate(locale, "result.title"))
        st.write(translate_canonical_text(locale, result.title))
        _render_risk_status(result, locale)
        st.write(translate_canonical_text(locale, result.summary))

        metric_columns = st.columns(2)
        with metric_columns[0]:
            st.metric(
                translate(locale, "result.risk_level"),
                translate_risk_level(locale, result.risk_level),
            )
        with metric_columns[1]:
            st.metric(
                translate(locale, "result.recommendation_priority"),
                translate_priority(locale, result.recommendation_priority),
            )

        st.write(translate(locale, "result.objective"))
        st.write(translate_canonical_text(locale, result.objective))

    with st.container(border=True):
        st.subheader(translate(locale, "result.model_predictions"))
        model_columns = st.columns(2)
        with model_columns[0]:
            _render_model_result(result.gradient_boosting, locale)
        with model_columns[1]:
            _render_model_result(result.decision_tree, locale)

        st.write(translate(locale, "result.model_agreement"))
        st.write(translate_canonical_text(locale, result.model_agreement))

    with st.container(border=True):
        st.subheader(translate(locale, "result.recommended_actions"))
        st.write(translate(locale, "result.objective"))
        st.write(translate_canonical_text(locale, result.objective))
        _render_items(result.recommendations, locale)
        st.write(translate(locale, "result.expected_outcome"))
        st.write(translate_canonical_text(locale, result.expected_outcome))

    with st.expander(translate(locale, "result.analysis_details"), expanded=False):
        st.write(translate(locale, "result.evidence"))
        _render_items(result.evidence, locale)
        st.write(translate(locale, "result.business_rationale"))
        _render_items(result.rationale, locale)

    with st.expander(translate(locale, "result.how_produced"), expanded=False):
        st.write(translate(locale, "result.flow"))

    st.info(translate(locale, "result.disclaimer"))


def _render_risk_status(result: PresentationResult, locale: Locale) -> None:
    message = translate_format(
        locale,
        "result.risk_status",
        risk_level=translate_risk_level(locale, result.risk_level),
    )
    if result.risk_level is RiskLevel.LOW:
        st.success(message)
    elif result.risk_level is RiskLevel.MODERATE:
        st.info(message)
    elif result.risk_level is RiskLevel.HIGH:
        st.warning(message)
    else:
        st.error(message)


def _render_model_result(model: ModelPresentationResult, locale: Locale) -> None:
    with st.container(border=True):
        st.write(model.display_name)
        st.metric(
            translate(locale, "result.prediction"),
            translate_prediction_label(locale, model.predicted_label),
        )
        st.caption(
            translate_format(
                locale,
                "result.predicted_class",
                predicted_class=model.predicted_class,
            )
        )
        if model.churn_probability is None:
            st.write(translate(locale, "result.probability_unavailable"))
            return

        percentage = model.churn_probability * 100
        st.write(
            translate_format(
                locale,
                "result.churn_probability",
                probability=f"{percentage:.1f}%",
            )
        )
        st.progress(round(percentage))


def _render_items(items: Iterable[str], locale: Locale) -> None:
    items = tuple(items)
    if not items:
        st.write("No items available.")
        return
    st.markdown(
        "\n".join(f"- {translate_canonical_text(locale, item)}" for item in items)
    )
