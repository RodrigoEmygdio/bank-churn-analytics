"""Integration-level input contract tests using real repository metadata."""

from __future__ import annotations

import pandas as pd

from churn_app.domain import CustomerInput
from churn_app.services.artifact_loader import load_metadata
from churn_app.services.input_builder import build_model_input


def test_customer_input_builds_model_ready_dataframe_with_real_metadata() -> None:
    metadata = load_metadata()
    customer = CustomerInput(
        credit_score=642,
        geography="France",
        gender="Male",
        age=48,
        tenure=9,
        balance=118317.27,
        num_of_products=4,
        has_cr_card=0,
        is_active_member=0,
        estimated_salary=78702.98,
    )

    frame = build_model_input(customer, metadata)

    assert isinstance(frame, pd.DataFrame)
    assert frame.shape == (1, 11)
    assert list(frame.columns) == list(metadata.input_schema.feature_names)
    assert frame.loc[0, "ProductsGroup"] == "3+"
    assert "Exited" not in frame.columns
