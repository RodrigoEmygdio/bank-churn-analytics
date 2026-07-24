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
    ModelPresentationResult,
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
        "Balance",
        "Estimated Salary",
        "Tenure",
    ]
    assert fake_streamlit.select_labels == [
        "Geography",
        "Gender",
        "Number of Products",
    ]
    assert fake_streamlit.checkbox_labels == ["Credit Card", "Active Member"]
    assert fake_streamlit.column_calls == [(2,), (2,), (2,), (2,), (2,)]


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

    rendered_values = [call[1] for call in fake_streamlit.calls]
    assert presentation.title in rendered_values
    assert presentation.summary in rendered_values
    assert "Analysis Result" in rendered_values
    assert "Risk Level" in rendered_values
    assert presentation.risk_level.value in rendered_values
    assert f"Risk Level: {presentation.risk_level.value}" in rendered_values
    assert "Model Agreement" in rendered_values
    assert presentation.model_agreement in rendered_values
    assert "Model Predictions" in rendered_values
    assert presentation.gradient_boosting.display_name in rendered_values
    assert presentation.decision_tree.display_name in rendered_values
    assert presentation.gradient_boosting.predicted_label in rendered_values
    assert presentation.decision_tree.predicted_label in rendered_values
    assert "Class: 1" in rendered_values
    assert "Class: 0" in rendered_values
    assert "Churn probability: 61.7%" in rendered_values
    assert "Churn probability: Probability unavailable" in rendered_values
    assert rendered_values.count("Recommendation Priority") == 1
    assert presentation.recommendation_priority.value in rendered_values
    assert "Objective" in rendered_values
    assert presentation.objective in rendered_values
    assert "Recommended Actions" in rendered_values
    assert "Evidence" in rendered_values
    assert "Business Rationale" in rendered_values
    assert "Expected Outcome" in rendered_values
    assert presentation.expected_outcome in rendered_values
    assert (
        "\n".join(f"- {item}" for item in presentation.recommendations)
        in rendered_values
    )
    assert "\n".join(f"- {item}" for item in presentation.evidence) in rendered_values
    assert "\n".join(f"- {item}" for item in presentation.rationale) in rendered_values
    for item in presentation.recommendations:
        assert _rendered_item_count(fake_streamlit.calls, item) == 1
    for item in presentation.evidence:
        assert _rendered_item_count(fake_streamlit.calls, item) == 1
    for item in presentation.rationale:
        assert _rendered_item_count(fake_streamlit.calls, item) == 1
    assert ("progress", 62) in fake_streamlit.calls
    assert fake_streamlit.expanders == [
        ("Analysis Details", False),
        ("How this analysis is produced", False),
    ]


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
        received_prediction: object,
        received_interpretation: object,
        received_recommendation: object,
    ) -> PresentationResult:
        calls.append("build_presentation")
        assert received_prediction is prediction_result
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
        "layout": "wide",
    }
    assert fake_streamlit.column_calls == [([0.9, 1.1], "large")]
    assert fake_streamlit.rendered_result is presentation
    assert fake_streamlit.render_result_calls == 1
    assert fake_streamlit.errors == []
    assert fake_streamlit.successes == ["Analysis completed."]


def test_main_renders_placeholder_before_analysis(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_streamlit = _FakeAppStreamlit()
    monkeypatch.setattr(app, "st", fake_streamlit)
    monkeypatch.setattr(app, "render_customer_form", lambda: None)

    def fail_if_called(customer: CustomerInput) -> PresentationResult:
        raise AssertionError("pipeline must not run before submit")

    monkeypatch.setattr(app, "run_pipeline", fail_if_called)

    app.main()

    assert fake_streamlit.infos == [
        "Complete the customer form and select Analyze Customer to generate the churn risk analysis."
    ]
    assert fake_streamlit.rendered_result is None


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
        self.column_calls: list[tuple[object, ...]] = []

    def form(self, key: str) -> _FormContext:
        self.form_key = key
        return _FormContext()

    def columns(self, spec: object, **kwargs: object) -> tuple[_FormContext, ...]:
        self.column_calls.append((spec,))
        if isinstance(spec, int):
            return tuple(_FormContext() for _ in range(spec))
        return tuple(_FormContext() for _ in spec)  # type: ignore[arg-type]

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

    def form_submit_button(self, label: str, **kwargs: object) -> bool:
        self.button_labels.append(label)
        return self.submitted


class _FakeRenderStreamlit:
    def __init__(self) -> None:
        self.calls: list[tuple[object, ...]] = []

    def header(self, value: str) -> None:
        self.calls.append(("header", value))

    def subheader(self, value: str) -> None:
        self.calls.append(("subheader", value))

    def write(self, value: str) -> None:
        self.calls.append(("write", value))

    def markdown(self, value: str) -> None:
        self.calls.append(("markdown", value))

    def success(self, value: str) -> None:
        self.calls.append(("success", value))

    def info(self, value: str) -> None:
        self.calls.append(("info", value))

    def warning(self, value: str) -> None:
        self.calls.append(("warning", value))

    def error(self, value: str) -> None:
        self.calls.append(("error", value))

    def caption(self, value: str) -> None:
        self.calls.append(("caption", value))

    def metric(self, label: str, value: str) -> None:
        self.calls.append(("metric", label))
        self.calls.append(("metric", value))

    def progress(self, value: int) -> None:
        self.calls.append(("progress", value))

    def columns(self, spec: object, **kwargs: object) -> tuple[_FormContext, ...]:
        if isinstance(spec, int):
            return tuple(_FormContext() for _ in range(spec))
        return tuple(_FormContext() for _ in spec)  # type: ignore[arg-type]

    def container(self, **kwargs: object) -> _FormContext:
        return _FormContext()

    @property
    def expanders(self) -> list[tuple[str, bool]]:
        return [(call[1], call[2]) for call in self.calls if call[0] == "expander"]

    def expander(self, label: str, *, expanded: bool = False) -> _FormContext:
        self.calls.append(("expander", label, expanded))
        return _FormContext()


class _FakeAppStreamlit:
    def __init__(self) -> None:
        self.page_config: dict[str, object] | None = None
        self.titles: list[str] = []
        self.writes: list[str] = []
        self.errors: list[str] = []
        self.infos: list[str] = []
        self.successes: list[str] = []
        self.column_calls: list[tuple[object, object]] = []
        self.rendered_result: PresentationResult | None = None
        self.render_result_calls = 0

    def set_page_config(self, **kwargs: object) -> None:
        self.page_config = kwargs

    def title(self, value: str) -> None:
        self.titles.append(value)

    def write(self, value: str) -> None:
        self.writes.append(value)

    def error(self, value: str) -> None:
        self.errors.append(value)

    def info(self, value: str) -> None:
        self.infos.append(value)

    def success(self, value: str) -> None:
        self.successes.append(value)

    def columns(self, spec: object, **kwargs: object) -> tuple[_FormContext, ...]:
        self.column_calls.append((spec, kwargs.get("gap")))
        if isinstance(spec, int):
            return tuple(_FormContext() for _ in range(spec))
        return tuple(_FormContext() for _ in spec)  # type: ignore[arg-type]

    def render_result(self, result: PresentationResult) -> None:
        self.render_result_calls += 1
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
        gradient_boosting=ModelPresentationResult(
            display_name="Gradient Boosting",
            predicted_class=1,
            predicted_label="Churn",
            churn_probability=0.617,
        ),
        decision_tree=ModelPresentationResult(
            display_name="Decision Tree",
            predicted_class=0,
            predicted_label="Retention",
            churn_probability=None,
        ),
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


def _rendered_item_count(calls: list[tuple[object, ...]], item: str) -> int:
    return sum(
        str(value).splitlines().count(f"- {item}")
        for _, value, *extra in calls
        if not extra and isinstance(value, str)
    )
