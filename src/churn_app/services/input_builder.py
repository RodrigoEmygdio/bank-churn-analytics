"""Input-construction service boundary.

Future stages will validate customer inputs, enforce approved training
categories, derive ProductsGroup, and build the one-row inference DataFrame in
metadata schema order.
"""

from __future__ import annotations

from typing import Any

from churn_app.domain import CustomerInput


def build_inference_input(customer: CustomerInput, metadata: dict[str, Any]) -> object:
    """Build the future inference input object from validated customer data.

    TODO(Prompt 4): Implement validation, ProductsGroup derivation, and
    DataFrame construction.
    """
    raise NotImplementedError("Input construction is deferred to Prompt 4.")
