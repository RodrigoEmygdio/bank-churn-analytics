"""Unit tests for the Streamlit presentation boundary."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pytest

import app
import churn_app.ui.form as form_module
import churn_app.ui.result as result_module
from churn_app.domain import (
    CustomerInput,
    PresentationResult,
    RecommendationPriority,
    RiskLevel,
)
from churn_app.services.prediction_service import PredictionError


def test_customer_form_returns_customer_input_when_submitted(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_streamlit = _FakeFormStreamlit(submitted=True)
    monkeypatch.setattr(form_module, "st", fake_streamlit)

    customer = form_module.render_customer_form()

    assert customer == CustomerInput(
        credit_score=650,
        geography="Germany",
        gender="Female",
        age=42,
        tenure=3,
        balance=1000.5,
        num_of_products=2,
        has_cr_card=1,
        is_active_member=0,
        estimated_salary=50000.0,
    )
    assert fake_streamlit.form_key == "customer-analysis-form"
    assert fake_streamlit.button_labels == ["Analyze Customer"]
    assert fake_streamlit.number_labels == [
        "Credit Score",
        "Age",
        "Tenure",
        "Balance",
        "Estimated Salary",
    ]
    assert fake_streamlit.select_labels == [
        "Geography",
        "Gender",
        "Number of Products",
    ]
    assert fake_streamlit.checkbox_labels == ["Credit Card", "Active Member"]


def test_customer_form_returns_none_before_submit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(form_module, "st", _FakeFormStreamlit(submitted=False))

    assert form_module.render_customer_form() is None


def test_render_result_displays_every_presentation_field(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_streamlit = _FakeRenderStreamlit()
    monkeypatch.setattr(result_module, "st", fake_streamlit)
    presentation = _presentation_result()

    result_module.render_result(presentation)

    rendered_values = [value for _, value in fake_streamlit.calls]
    assert presentation.title in rendered_values
    assert presentation.summary in rendered_values
    assert "Risk Level" in rendered_values
    assert presentation.risk_level.value in rendered_values
    assert "Model Agreement" in rendered_values
    assert presentation.model_agreement in rendered_values
    assert "Evidence" in rendered_values
    assert "Business Rationale" in rendered_values
    assert "Recommendation Priority" in rendered_values
    assert presentation.recommendation_priority.value in rendered_values
    assert "Objective" in rendered_values
    assert presentation.objective in rendered_values
    assert "Recommendations" in rendered_values
    assert "Expected Outcome" in rendered_values
    assert presentation.expected_outcome in rendered_values
    for item in (
        presentation.evidence + presentation.rationale + presentation.recommendations
    ):
        assert f"- {item}" in rendered_values


def test_run_pipeline_invokes_approved_services_in_order(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    customer = _customer_input()
    metadata = object()
    loaded_artifacts = _LoadedArtifactsDouble(metadata=metadata)
    model_input = object()
    prediction_result = object()
    risk_level = object()
    interpretation = object()
    recommendation = object()
    presentation = _presentation_result()
    calls: list[str] = []

    def load_model_artifacts() -> _LoadedArtifactsDouble:
        calls.append("load_model_artifacts")
        return loaded_artifacts

    def build_model_input(
        received_customer: CustomerInput,
        received_metadata: object,
    ) -> object:
        calls.append("build_model_input")
        assert received_customer is customer
        assert received_metadata is metadata
        return model_input

    def predict(received_artifacts: object, received_model_input: object) -> object:
        calls.append("predict")
        assert received_artifacts is loaded_artifacts
        assert received_model_input is model_input
        return prediction_result

    def determine_risk_level(received_prediction: object) -> object:
        calls.append("determine_risk_level")
        assert received_prediction is prediction_result
        return risk_level

    def interpret_risk(
        received_prediction: object,
        received_risk_level: object,
    ) -> object:
        calls.append("interpret_risk")
        assert received_prediction is prediction_result
        assert received_risk_level is risk_level
        return interpretation

    def generate_recommendation(received_interpretation: object) -> object:
        calls.append("generate_recommendation")
        assert received_interpretation is interpretation
        return recommendation

    def build_presentation(
        received_interpretation: object,
        received_recommendation: object,
    ) -> PresentationResult:
        calls.append("build_presentation")
        assert received_interpretation is interpretation
        assert received_recommendation is recommendation
        return presentation

    monkeypatch.setattr(app, "load_model_artifacts", load_model_artifacts)
    monkeypatch.setattr(app, "build_model_input", build_model_input)
    monkeypatch.setattr(app, "predict", predict)
    monkeypatch.setattr(app, "determine_risk_level", determine_risk_level)
    monkeypatch.setattr(app, "interpret_risk", interpret_risk)
    monkeypatch.setattr(app, "generate_recommendation", generate_recommendation)
    monkeypatch.setattr(app, "build_presentation", build_presentation)

    result = app.run_pipeline(customer)

    assert result is presentation
    assert calls == [
        "load_model_artifacts",
        "build_model_input",
        "predict",
        "determine_risk_level",
        "interpret_risk",
        "generate_recommendation",
        "build_presentation",
    ]


def test_main_renders_pipeline_result(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_streamlit = _FakeAppStreamlit()
    customer = _customer_input()
    presentation = _presentation_result()

    monkeypatch.setattr(app, "st", fake_streamlit)
    monkeypatch.setattr(app, "render_customer_form", lambda: customer)
    monkeypatch.setattr(app, "run_pipeline", lambda received: presentation)
    monkeypatch.setattr(app, "render_result", fake_streamlit.render_result)

    app.main()

    assert fake_streamlit.page_config == {
        "page_title": "Bank Churn Risk Analysis",
        "layout": "centered",
    }
    assert fake_streamlit.rendered_result is presentation
    assert fake_streamlit.errors == []


def test_main_renders_service_error_without_traceback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_streamlit = _FakeAppStreamlit()
    monkeypatch.setattr(app, "st", fake_streamlit)
    monkeypatch.setattr(app, "render_customer_form", _customer_input)

    def fail_pipeline(customer: CustomerInput) -> PresentationResult:
        raise PredictionError("pipeline failed")

    monkeypatch.setattr(app, "run_pipeline", fail_pipeline)

    app.main()

    assert fake_streamlit.errors == [
        "The prediction service could not produce a valid model result."
    ]


def test_main_renders_unexpected_error_without_traceback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_streamlit = _FakeAppStreamlit()
    monkeypatch.setattr(app, "st", fake_streamlit)
    monkeypatch.setattr(app, "render_customer_form", _customer_input)

    def fail_pipeline(customer: CustomerInput) -> PresentationResult:
        raise ValueError("sensitive details")

    monkeypatch.setattr(app, "run_pipeline", fail_pipeline)

    app.main()

    assert fake_streamlit.errors == ["Unexpected internal error."]


def test_main_converts_result_rendering_exception_to_generic_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_streamlit = _FakeAppStreamlit()
    monkeypatch.setattr(app, "st", fake_streamlit)
    monkeypatch.setattr(app, "render_customer_form", _customer_input)
    monkeypatch.setattr(app, "run_pipeline", lambda customer: _presentation_result())

    def fail_rendering(presentation: PresentationResult) -> None:
        raise ValueError("rendering internals")

    monkeypatch.setattr(app, "render_result", fail_rendering)

    app.main()

    assert fake_streamlit.errors == ["Unexpected internal error."]


def test_ui_modules_do_not_import_service_boundaries() -> None:
    for path in (Path("src/churn_app/ui/form.py"), Path("src/churn_app/ui/result.py")):
        source = path.read_text(encoding="utf-8")

        assert "churn_app.services" not in source


class _FormContext:
    def __enter__(self) -> None:
        return None

    def __exit__(self, *args: object) -> None:
        return None


class _FakeFormStreamlit:
    def __init__(self, *, submitted: bool) -> None:
        self.submitted = submitted
        self.form_key: str | None = None
        self.button_labels: list[str] = []
        self.number_labels: list[str] = []
        self.select_labels: list[str] = []
        self.checkbox_labels: list[str] = []

    def form(self, key: str) -> _FormContext:
        self.form_key = key
        return _FormContext()

    def number_input(self, label: str, **kwargs: object) -> int | float:
        self.number_labels.append(label)
        return {
            "Credit Score": 650,
            "Age": 42,
            "Tenure": 3,
            "Balance": 1000.5,
            "Estimated Salary": 50000.0,
        }[label]

    def selectbox(self, label: str, options: tuple[object, ...]) -> object:
        self.select_labels.append(label)
        selected = {
            "Geography": "Germany",
            "Gender": "Female",
            "Number of Products": 2,
        }[label]
        assert selected in options
        return selected

    def checkbox(self, label: str) -> bool:
        self.checkbox_labels.append(label)
        return label == "Credit Card"

    def form_submit_button(self, label: str) -> bool:
        self.button_labels.append(label)
        return self.submitted


class _FakeRenderStreamlit:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []

    def header(self, value: str) -> None:
        self.calls.append(("header", value))

    def subheader(self, value: str) -> None:
        self.calls.append(("subheader", value))

    def write(self, value: str) -> None:
        self.calls.append(("write", value))

    def markdown(self, value: str) -> None:
        self.calls.append(("markdown", value))


class _FakeAppStreamlit:
    def __init__(self) -> None:
        self.page_config: dict[str, object] | None = None
        self.titles: list[str] = []
        self.writes: list[str] = []
        self.errors: list[str] = []
        self.rendered_result: PresentationResult | None = None

    def set_page_config(self, **kwargs: object) -> None:
        self.page_config = kwargs

    def title(self, value: str) -> None:
        self.titles.append(value)

    def write(self, value: str) -> None:
        self.writes.append(value)

    def error(self, value: str) -> None:
        self.errors.append(value)

    def render_result(self, result: PresentationResult) -> None:
        self.rendered_result = result


@dataclass(frozen=True, slots=True)
class _LoadedArtifactsDouble:
    metadata: object


def _customer_input() -> CustomerInput:
    return CustomerInput(
        credit_score=650,
        geography="Germany",
        gender="Female",
        age=42,
        tenure=3,
        balance=1000.5,
        num_of_products=2,
        has_cr_card=1,
        is_active_member=0,
        estimated_salary=50000.0,
    )


def _presentation_result() -> PresentationResult:
    return PresentationResult(
        risk_level=RiskLevel.HIGH,
        title="High Churn Risk",
        summary="The primary prediction model detected evidence associated with customer churn.",
        model_agreement="Only the primary model predicted churn.",
        evidence=(
            "Gradient Boosting predicted churn.",
            "Decision Tree predicted retention.",
        ),
        rationale=(
            "The primary model detected churn.",
            "The complementary model did not confirm the prediction.",
            "This disagreement corresponds to high churn risk.",
        ),
        recommendation_priority=RecommendationPriority.HIGH,
        objective="Reduce customer churn risk through proactive engagement.",
        recommendations=(
            "Contact the customer.",
            "Review customer satisfaction.",
            "Evaluate appropriate retention actions.",
        ),
        expected_outcome="Customer retention opportunities are identified before churn occurs.",
    )
