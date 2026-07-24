"""Locale contract for supported UI languages."""

from __future__ import annotations

from enum import StrEnum


class Locale(StrEnum):
    """Closed set of supported interface locales."""

    EN = "en"
    PT_BR = "pt-BR"
