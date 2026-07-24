"""Streamlit entry point for the bank churn decision-support application.

This module composes the approved application pipeline and delegates all
validation, inference, decision, interpretation, recommendation, and
presentation-contract construction to the service boundaries.
"""

from __future__ import annotations

import streamlit as st

from churn_app.domain import CustomerInput, PresentationResult
from churn_app.i18n import Locale, translate
from churn_app.services.artifact_loader import ArtifactError, load_model_artifacts
from churn_app.services.decision_policy import (
    DecisionPolicyError,
    determine_risk_level,
)
from churn_app.services.input_builder import InputValidationError, build_model_input
from churn_app.services.prediction_service import PredictionError, predict
from churn_app.services.presentation_layer import (
    PresentationLayerError,
    build_presentation,
)
from churn_app.services.recommendation_engine import (
    RecommendationEngineError,
    generate_recommendation,
)
from churn_app.services.risk_interpreter import RiskInterpreterError, interpret_risk
from churn_app.ui.form import render_customer_form
from churn_app.ui.result import render_result

_LOCALE_BY_LABEL = {
    "English": Locale.EN,
    "Português (Brasil)": Locale.PT_BR,
}
_LABEL_BY_LOCALE = {locale: label for label, locale in _LOCALE_BY_LABEL.items()}


def run_pipeline(customer: CustomerInput) -> PresentationResult:
    """Run the approved service pipeline for one validated form submission."""
    loaded_artifacts = load_model_artifacts()
    model_input = build_model_input(customer, loaded_artifacts.metadata)
    prediction_result = predict(loaded_artifacts, model_input)
    risk_level = determine_risk_level(prediction_result)
    interpretation = interpret_risk(prediction_result, risk_level)
    recommendation = generate_recommendation(interpretation)
    return build_presentation(prediction_result, interpretation, recommendation)


def main() -> None:
    """Render the Streamlit interface and delegate submitted data to services."""
    locale = render_language_selector()
    st.set_page_config(
        page_title=translate(locale, "app.title"),
        layout="wide",
    )
    st.title(translate(locale, "app.title"))
    st.write(translate(locale, "app.description"))

    form_column, result_column = st.columns([0.9, 1.1], gap="large")
    with form_column:
        customer = render_customer_form(locale)

    with result_column:
        if customer is None:
            st.info(translate(locale, "result.placeholder"))
            return

        try:
            presentation = run_pipeline(customer)
            st.success(translate(locale, "result.completed"))
            render_result(presentation, locale)
        except InputValidationError:
            st.error(translate(locale, "error.invalid_input"))
        except ArtifactError:
            st.error(translate(locale, "error.artifact"))
        except PredictionError:
            st.error(translate(locale, "error.prediction"))
        except DecisionPolicyError:
            st.error(translate(locale, "error.decision_policy"))
        except RiskInterpreterError:
            st.error(translate(locale, "error.interpretation"))
        except RecommendationEngineError:
            st.error(translate(locale, "error.recommendation"))
        except PresentationLayerError:
            st.error(translate(locale, "error.presentation"))
        except Exception:  # noqa: BLE001 - UI boundary must hide unexpected tracebacks.
            st.error(translate(locale, "error.unexpected"))


def render_language_selector() -> Locale:
    """Render and persist the selected UI locale."""
    current_locale = st.session_state.get("locale", Locale.EN)
    if type(current_locale) is not Locale:
        current_locale = Locale.EN

    options = list(_LOCALE_BY_LABEL)
    selected_label = st.sidebar.selectbox(
        translate(Locale.EN, "language.selector"),
        options,
        index=options.index(_LABEL_BY_LOCALE[current_locale]),
    )
    locale = _LOCALE_BY_LABEL[selected_label]
    st.session_state["locale"] = locale
    return locale


if __name__ == "__main__":
    main()
