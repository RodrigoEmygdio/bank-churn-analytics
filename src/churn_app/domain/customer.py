"""Customer input contract for the churn application.

The contract represents only user-provided business inputs approved by the
metadata schema. Internally derived features such as ProductsGroup are
intentionally excluded and belong to the input-construction service.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CustomerInput:
    """User-facing customer attributes before validation and feature derivation.

    The dataclass is immutable and structurally typed, but comprehensive
    validation is intentionally deferred to `services.input_builder`.
    """

    credit_score: int
    geography: str
    gender: str
    age: int
    tenure: int
    balance: float
    num_of_products: int
    has_cr_card: int
    is_active_member: int
    estimated_salary: float
