"""Deterministic translation API for supported UI locales."""

from __future__ import annotations

from string import Formatter

from churn_app.domain import RecommendationPriority, RiskLevel
from churn_app.i18n.catalog import CANONICAL_TEXT_KEYS, CATALOG
from churn_app.i18n.locale import Locale


class TranslationError(Exception):
    """Base exception for deterministic translation failures."""


class UnsupportedLocaleError(TranslationError):
    """Raised when a locale is not supported."""


class MissingTranslationError(TranslationError):
    """Raised when a catalog key or canonical text is missing."""


class TranslationFormatError(TranslationError):
    """Raised when a formatted translation cannot be rendered."""


def translate(locale: Locale, key: str) -> str:
    """Return one translated string for a supported locale and key."""
    _validate_locale(locale)
    try:
        return CATALOG[locale][key]
    except KeyError as exc:
        raise MissingTranslationError(
            f"missing translation for locale={locale.value}, key={key!r}"
        ) from exc


def translate_format(locale: Locale, key: str, **values: object) -> str:
    """Return one translated string after deterministic placeholder formatting."""
    template = translate(locale, key)
    expected_placeholders = _placeholders(template)
    supplied_placeholders = set(values)
    if expected_placeholders != supplied_placeholders:
        raise TranslationFormatError(
            f"translation {key!r} expected placeholders "
            f"{sorted(expected_placeholders)}, got {sorted(supplied_placeholders)}"
        )
    try:
        return template.format(**values)
    except (KeyError, ValueError) as exc:
        raise TranslationFormatError(f"could not format translation {key!r}") from exc


def translate_canonical_text(locale: Locale, text: str) -> str:
    """Translate exact canonical business text produced by domain services."""
    try:
        key = CANONICAL_TEXT_KEYS[text]
    except KeyError as exc:
        raise MissingTranslationError(
            f"canonical text has no translation key: {text!r}"
        ) from exc
    return translate(locale, key)


def translate_risk_level(locale: Locale, risk_level: RiskLevel) -> str:
    """Translate one risk-level enum value for display only."""
    if type(risk_level) is not RiskLevel:
        raise TranslationError("risk_level must be a RiskLevel.")
    return translate(locale, f"risk.{risk_level.value.lower()}")


def translate_priority(locale: Locale, priority: RecommendationPriority) -> str:
    """Translate one recommendation-priority enum value for display only."""
    if type(priority) is not RecommendationPriority:
        raise TranslationError("priority must be a RecommendationPriority.")
    return translate(locale, f"priority.{priority.value.lower()}")


def translate_prediction_label(locale: Locale, label: str) -> str:
    """Translate one canonical model prediction label for display only."""
    key = {
        "Retention": "prediction.retention",
        "Churn": "prediction.churn",
    }.get(label)
    if key is None:
        raise MissingTranslationError(f"unsupported prediction label: {label!r}")
    return translate(locale, key)


def _validate_locale(locale: object) -> None:
    if type(locale) is not Locale:
        raise UnsupportedLocaleError(f"unsupported locale: {locale!r}")
    if locale not in CATALOG:
        raise UnsupportedLocaleError(f"unsupported locale: {locale!r}")


def _placeholders(template: str) -> set[str]:
    return {
        field_name
        for _, field_name, _, _ in Formatter().parse(template)
        if field_name is not None
    }
