"""Customer form presentation boundary for the Streamlit application.

This module collects user-facing values and creates `CustomerInput`. It does
not implement domain validation, feature construction, or inference.
"""

from __future__ import annotations

import streamlit as st

from churn_app.domain import CustomerInput

GEOGRAPHIES = ("France", "Germany", "Spain")
GENDERS = ("Female", "Male")
PRODUCT_COUNTS = (1, 2, 3, 4)


def render_customer_form() -> CustomerInput | None:
    """Render the customer form and return submitted user input."""
    with st.form("customer-analysis-form"):
        left, right = st.columns(2)
        with left:
            credit_score = st.number_input("Credit Score", value=650, step=1)
        with right:
            age = st.number_input("Age", value=40, step=1)

        left, right = st.columns(2)
        with left:
            geography = st.selectbox("Geography", GEOGRAPHIES)
        with right:
            gender = st.selectbox("Gender", GENDERS)

        left, right = st.columns(2)
        with left:
            balance = st.number_input("Balance", value=0.0, step=100.0)
        with right:
            estimated_salary = st.number_input(
                "Estimated Salary",
                value=0.0,
                step=100.0,
            )

        left, right = st.columns(2)
        with left:
            tenure = st.number_input("Tenure", value=0, step=1)
        with right:
            num_of_products = st.selectbox("Number of Products", PRODUCT_COUNTS)

        left, right = st.columns(2)
        with left:
            has_cr_card = st.checkbox("Credit Card")
        with right:
            is_active_member = st.checkbox("Active Member")

        submitted = st.form_submit_button(
            "Analyze Customer",
            use_container_width=True,
        )

    if not submitted:
        return None

    return CustomerInput(
        credit_score=int(credit_score),
        geography=geography,
        gender=gender,
        age=int(age),
        tenure=int(tenure),
        balance=float(balance),
        num_of_products=int(num_of_products),
        has_cr_card=int(has_cr_card),
        is_active_member=int(is_active_member),
        estimated_salary=float(estimated_salary),
    )
