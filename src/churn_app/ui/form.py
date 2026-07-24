"""Customer form presentation boundary for the Streamlit application.

This module collects user-facing values and creates `CustomerInput`. It does
not implement domain validation, feature construction, or inference.
"""

from __future__ import annotations

import streamlit as st

from churn_app.domain import CustomerInput
from churn_app.i18n import Locale, translate

GEOGRAPHIES = ("France", "Germany", "Spain")
GENDERS = ("Female", "Male")
PRODUCT_COUNTS = (1, 2, 3, 4)

_GEOGRAPHY_LABEL_KEYS = {
    "France": "option.geography.france",
    "Germany": "option.geography.germany",
    "Spain": "option.geography.spain",
}
_GENDER_LABEL_KEYS = {
    "Female": "option.gender.female",
    "Male": "option.gender.male",
}


def render_customer_form(locale: Locale) -> CustomerInput | None:
    """Render the customer form and return submitted user input."""
    with st.form("customer-analysis-form"):
        st.subheader(translate(locale, "form.title"))
        left, right = st.columns(2)
        with left:
            credit_score = st.number_input(
                translate(locale, "form.credit_score"),
                value=650,
                step=1,
            )
        with right:
            age = st.number_input(translate(locale, "form.age"), value=40, step=1)

        left, right = st.columns(2)
        with left:
            geography_options = _localized_options(locale, _GEOGRAPHY_LABEL_KEYS)
            geography_label = st.selectbox(
                translate(locale, "form.geography"),
                tuple(geography_options),
            )
        with right:
            gender_options = _localized_options(locale, _GENDER_LABEL_KEYS)
            gender_label = st.selectbox(
                translate(locale, "form.gender"),
                tuple(gender_options),
            )

        left, right = st.columns(2)
        with left:
            balance = st.number_input(
                translate(locale, "form.balance"),
                value=0.0,
                step=100.0,
            )
        with right:
            estimated_salary = st.number_input(
                translate(locale, "form.estimated_salary"),
                value=0.0,
                step=100.0,
            )

        left, right = st.columns(2)
        with left:
            tenure = st.number_input(
                translate(locale, "form.tenure"),
                value=0,
                step=1,
            )
        with right:
            num_of_products = st.selectbox(
                translate(locale, "form.number_of_products"),
                PRODUCT_COUNTS,
            )

        left, right = st.columns(2)
        with left:
            has_cr_card = st.checkbox(translate(locale, "form.credit_card"))
        with right:
            is_active_member = st.checkbox(translate(locale, "form.active_member"))

        submitted = st.form_submit_button(
            translate(locale, "form.submit"),
            use_container_width=True,
        )

    if not submitted:
        return None

    return CustomerInput(
        credit_score=int(credit_score),
        geography=geography_options[geography_label],
        gender=gender_options[gender_label],
        age=int(age),
        tenure=int(tenure),
        balance=float(balance),
        num_of_products=int(num_of_products),
        has_cr_card=int(has_cr_card),
        is_active_member=int(is_active_member),
        estimated_salary=float(estimated_salary),
    )


def _localized_options(locale: Locale, label_keys: dict[str, str]) -> dict[str, str]:
    return {translate(locale, key): value for value, key in label_keys.items()}
