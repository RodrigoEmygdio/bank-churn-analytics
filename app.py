"""Streamlit entry point for the bank churn decision-support application.

This module composes the approved application pipeline and delegates all
validation, inference, decision, interpretation, recommendation, and
presentation-contract construction to the service boundaries.
"""

from __future__ import annotations

import streamlit as st

from churn_app.domain import CustomerInput, PresentationResult
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
    st.set_page_config(
        page_title="Bank Churn Risk Analysis",
        layout="wide",
    )
    st.title("Bank Churn Risk Analysis")
    st.write(
        "Academic decision-support interface for analyzing bank customer churn risk."
    )

    form_column, result_column = st.columns([0.9, 1.1], gap="large")
    with form_column:
        customer = render_customer_form()

    with result_column:
        if customer is None:
            st.info(
                "Complete the customer form and select Analyze Customer to "
                "generate the churn risk analysis."
            )
            return

        try:
            presentation = run_pipeline(customer)
            st.success("Analysis completed.")
            render_result(presentation)
        except InputValidationError:
            st.error("Invalid customer input. Review the form values and try again.")
        except ArtifactError:
            st.error("Model artifacts are unavailable or failed integrity validation.")
        except PredictionError:
            st.error("The prediction service could not produce a valid model result.")
        except DecisionPolicyError:
            st.error("The risk decision policy could not process the model outputs.")
        except RiskInterpreterError:
            st.error("The risk interpretation could not be generated.")
        except RecommendationEngineError:
            st.error("The business recommendation could not be generated.")
        except PresentationLayerError:
            st.error("The presentation result could not be composed.")
        except Exception:  # noqa: BLE001 - UI boundary must hide unexpected tracebacks.
            st.error("Unexpected internal error.")


if __name__ == "__main__":
    main()
