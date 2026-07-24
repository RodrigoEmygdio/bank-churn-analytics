"""Deterministic internationalization support for UI rendering."""

from churn_app.i18n.locale import Locale
from churn_app.i18n.translator import (
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

__all__ = [
    "Locale",
    "MissingTranslationError",
    "TranslationError",
    "TranslationFormatError",
    "UnsupportedLocaleError",
    "translate",
    "translate_canonical_text",
    "translate_format",
    "translate_prediction_label",
    "translate_priority",
    "translate_risk_level",
]
