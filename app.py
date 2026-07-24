"""Minimal Streamlit entry point for the churn application scaffold.

This module composes the approved package boundaries without loading model
artifacts, collecting the final customer form, or executing inference.
"""

from __future__ import annotations


def main() -> None:
    """Render a neutral scaffold page for the future Streamlit application."""
    import streamlit as st

    st.set_page_config(
        page_title="Bank Churn Analytics",
        page_icon="",
        layout="centered",
    )
    st.title("Bank Churn Analytics")
    st.info(
        "Application scaffold ready. Prediction workflow, validation, and "
        "model orchestration will be implemented in later stages."
    )


if __name__ == "__main__":
    main()
