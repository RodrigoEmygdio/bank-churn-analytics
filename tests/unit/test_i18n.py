"""Unit tests for deterministic bilingual UI internationalization."""

from __future__ import annotations

from string import Formatter

import pytest

from churn_app.domain import (
    ModelIdentity,
    ModelPrediction,
    ModelRole,
    ModelType,
    PredictionResult,
    RiskLevel,
)
from churn_app.i18n import (
    Locale,
    MissingTranslationError,
    TranslationError,
    TranslationFormatError,
    UnsupportedLocaleError,
    translate,
    translate_canonical_text,
    translate_format,
    translate_prediction_label,
    translate_priority,
    translate_risk_level,
)
from churn_app.i18n.catalog import CATALOG, EN_TRANSLATIONS, PT_BR_TRANSLATIONS
from churn_app.services.recommendation_engine import generate_recommendation
from churn_app.services.risk_interpreter import interpret_risk

CASES = [
    (0, 0, RiskLevel.LOW),
    (0, 1, RiskLevel.MODERATE),
    (1, 0, RiskLevel.HIGH),
    (1, 1, RiskLevel.CRITICAL),
]


def test_locale_contains_exactly_supported_values() -> None:
    assert [locale.value for locale in Locale] == ["en", "pt-BR"]


def test_catalog_key_sets_match_and_values_are_not_empty() -> None:
    assert set(EN_TRANSLATIONS) == set(PT_BR_TRANSLATIONS)
    assert set(CATALOG[Locale.EN]) == set(CATALOG[Locale.PT_BR])
    assert len(EN_TRANSLATIONS) == len(set(EN_TRANSLATIONS))
    assert len(PT_BR_TRANSLATIONS) == len(set(PT_BR_TRANSLATIONS))

    for translations in CATALOG.values():
        assert all(value.strip() for value in translations.values())


def test_formatting_placeholders_match_across_locales() -> None:
    for key, english_value in EN_TRANSLATIONS.items():
        assert _placeholders(english_value) == _placeholders(PT_BR_TRANSLATIONS[key])


def test_translate_rejects_unknown_locale_and_key() -> None:
    with pytest.raises(UnsupportedLocaleError):
        translate("pt-BR", "app.title")  # type: ignore[arg-type]

    with pytest.raises(MissingTranslationError):
        translate(Locale.EN, "missing.key")


def test_translate_format_is_deterministic_and_validates_placeholders() -> None:
    first = translate_format(Locale.EN, "result.risk_status", risk_level="HIGH")
    second = translate_format(Locale.EN, "result.risk_status", risk_level="HIGH")

    assert first == second == "Risk Level: HIGH"
    with pytest.raises(TranslationFormatError):
        translate_format(Locale.EN, "result.risk_status", wrong="HIGH")


def test_enum_and_prediction_label_translation() -> None:
    assert translate_risk_level(Locale.PT_BR, RiskLevel.CRITICAL) == "CRÍTICO"
    assert (
        translate_priority(
            Locale.PT_BR,
            generate_recommendation(
                interpret_risk(_prediction_result(1, 1), RiskLevel.CRITICAL)
            ).priority,
        )
        == "URGENTE"
    )
    assert translate_prediction_label(Locale.PT_BR, "Retention") == "Retenção"
    assert translate_prediction_label(Locale.PT_BR, "Churn") == "Churn"

    with pytest.raises(TranslationError):
        translate_risk_level(Locale.EN, "HIGH")  # type: ignore[arg-type]
    with pytest.raises(MissingTranslationError):
        translate_prediction_label(Locale.EN, "Unknown")


@pytest.mark.parametrize(("gb_class", "dt_class", "risk_level"), CASES)
def test_all_canonical_business_content_has_translations(
    gb_class: int,
    dt_class: int,
    risk_level: RiskLevel,
) -> None:
    interpretation = interpret_risk(_prediction_result(gb_class, dt_class), risk_level)
    recommendation = generate_recommendation(interpretation)
    canonical_items = (
        interpretation.title,
        interpretation.summary,
        interpretation.model_agreement,
        *interpretation.evidence,
        *interpretation.rationale,
        recommendation.objective,
        *recommendation.recommendations,
        recommendation.expected_outcome,
    )

    for item in canonical_items:
        assert translate_canonical_text(Locale.EN, item) == item
        assert translate_canonical_text(Locale.PT_BR, item)


def test_unknown_canonical_business_text_fails() -> None:
    with pytest.raises(MissingTranslationError):
        translate_canonical_text(Locale.PT_BR, "Unmapped canonical text.")


def test_translator_has_no_streamlit_dependency() -> None:
    import ast
    from pathlib import Path

    for path in Path("src/churn_app/i18n").glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        imported_roots = {
            node.module.split(".", maxsplit=1)[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module
        }
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_roots.update(
                    alias.name.split(".", maxsplit=1)[0] for alias in node.names
                )

        assert imported_roots.isdisjoint(
            {"streamlit", "pandas", "numpy", "sklearn", "joblib"}
        )


def _prediction_result(gb_class: int, dt_class: int) -> PredictionResult:
    return PredictionResult(
        gradient_boosting=ModelPrediction(
            model=ModelIdentity(
                model_type=ModelType.GRADIENT_BOOSTING,
                role=ModelRole.PRIMARY,
                display_name="Gradient Boosting",
            ),
            predicted_class=gb_class,
            probability=0.5,
        ),
        decision_tree=ModelPrediction(
            model=ModelIdentity(
                model_type=ModelType.DECISION_TREE,
                role=ModelRole.SENSITIVITY_COMPLEMENT,
                display_name="Decision Tree",
            ),
            predicted_class=dt_class,
            probability=0.5,
        ),
    )


def _placeholders(value: str) -> set[str]:
    return {
        field_name
        for _, field_name, _, _ in Formatter().parse(value)
        if field_name is not None
    }
