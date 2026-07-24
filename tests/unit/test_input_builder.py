"""Unit tests for customer input validation and feature construction."""

from __future__ import annotations

from dataclasses import replace

import pandas as pd
import pytest

from churn_app.domain import CustomerInput
from churn_app.services.artifact_loader import (
    ArtifactMetadata,
    InputSchemaMetadata,
    load_metadata,
)
from churn_app.services.input_builder import (
    FeatureConstructionError,
    InputValidationError,
    InvalidFieldValueError,
    SchemaMismatchError,
    UnsupportedCategoryError,
    build_model_input,
    derive_products_group,
    validate_customer_input,
)


def test_valid_customer_input_is_accepted() -> None:
    validate_customer_input(_valid_customer())


@pytest.mark.parametrize(
    ("field", "value", "exception_type"),
    [
        ("credit_score", None, InvalidFieldValueError),
        ("credit_score", "650", InvalidFieldValueError),
        ("credit_score", 650.5, InvalidFieldValueError),
        ("credit_score", True, InvalidFieldValueError),
        ("credit_score", 0, InvalidFieldValueError),
        ("geography", "Portugal", UnsupportedCategoryError),
        ("geography", None, UnsupportedCategoryError),
        ("gender", "Other", UnsupportedCategoryError),
        ("gender", None, UnsupportedCategoryError),
        ("age", 0, InvalidFieldValueError),
        ("tenure", -1, InvalidFieldValueError),
        ("balance", -0.01, InvalidFieldValueError),
        ("balance", float("nan"), InvalidFieldValueError),
        ("balance", float("inf"), InvalidFieldValueError),
        ("balance", "100.0", InvalidFieldValueError),
        ("num_of_products", 1.8, InvalidFieldValueError),
        ("num_of_products", False, InvalidFieldValueError),
        ("has_cr_card", 2, InvalidFieldValueError),
        ("has_cr_card", True, InvalidFieldValueError),
        ("is_active_member", -1, InvalidFieldValueError),
        ("is_active_member", False, InvalidFieldValueError),
        ("estimated_salary", -1.0, InvalidFieldValueError),
        ("estimated_salary", float("-inf"), InvalidFieldValueError),
    ],
)
def test_invalid_customer_input_is_rejected(
    field: str, value: object, exception_type: type[InputValidationError]
) -> None:
    customer = replace(_valid_customer(), **{field: value})

    with pytest.raises(exception_type):
        validate_customer_input(customer)


@pytest.mark.parametrize(
    ("num_of_products", "expected_group"),
    [
        (1, "1"),
        (2, "2"),
        (3, "3+"),
        (4, "3+"),
    ],
)
def test_derive_products_group_matches_training_rule(
    num_of_products: int, expected_group: str
) -> None:
    # Evidence: notebooks/03_machine_learning.ipynb cell 9 maps 1, 2, 3, 4
    # to categories "1", "2", "3+", "3+".
    assert derive_products_group(num_of_products) == expected_group


@pytest.mark.parametrize("num_of_products", [0, -1, 5])
def test_derive_products_group_rejects_values_outside_training_rule(
    num_of_products: int,
) -> None:
    with pytest.raises((InvalidFieldValueError, FeatureConstructionError)):
        derive_products_group(num_of_products)


def test_build_model_input_returns_one_row_dataframe_in_metadata_order() -> None:
    metadata = load_metadata()
    customer = _valid_customer()

    frame = build_model_input(customer, metadata)

    assert isinstance(frame, pd.DataFrame)
    assert frame.shape == (1, metadata.input_schema.feature_count)
    assert list(frame.columns) == list(metadata.input_schema.feature_names)
    assert "Exited" not in frame.columns
    assert "ProductsGroup" in frame.columns
    assert frame.loc[0, "CreditScore"] == customer.credit_score
    assert frame.loc[0, "Geography"] == customer.geography
    assert frame.loc[0, "Gender"] == customer.gender
    assert frame.loc[0, "Age"] == customer.age
    assert frame.loc[0, "Tenure"] == customer.tenure
    assert frame.loc[0, "Balance"] == customer.balance
    assert frame.loc[0, "NumOfProducts"] == customer.num_of_products
    assert frame.loc[0, "HasCrCard"] == customer.has_cr_card
    assert frame.loc[0, "IsActiveMember"] == customer.is_active_member
    assert frame.loc[0, "EstimatedSalary"] == customer.estimated_salary
    assert frame.loc[0, "ProductsGroup"] == "2"


def test_build_model_input_applies_metadata_semantic_dtypes() -> None:
    frame = build_model_input(_valid_customer(), load_metadata())

    assert str(frame["CreditScore"].dtype) == "int64"
    assert str(frame["Age"].dtype) == "int64"
    assert str(frame["Tenure"].dtype) == "int64"
    assert str(frame["Balance"].dtype) == "float64"
    assert str(frame["EstimatedSalary"].dtype) == "float64"
    assert pd.api.types.is_string_dtype(frame["Geography"])
    assert pd.api.types.is_string_dtype(frame["Gender"])
    assert isinstance(frame["ProductsGroup"].dtype, pd.CategoricalDtype)
    assert list(frame["ProductsGroup"].cat.categories) == ["1", "2", "3+"]


def test_build_model_input_raises_on_feature_count_mismatch() -> None:
    metadata = load_metadata()
    bad_metadata = replace(
        metadata,
        input_schema=replace(metadata.input_schema, feature_count=999),
    )

    with pytest.raises(SchemaMismatchError):
        build_model_input(_valid_customer(), bad_metadata)


def test_build_model_input_raises_on_missing_declared_feature() -> None:
    metadata = load_metadata()
    feature_names = tuple(
        feature
        for feature in metadata.input_schema.feature_names
        if feature != "ProductsGroup"
    )
    bad_metadata = _replace_schema(metadata, feature_names=feature_names)

    with pytest.raises(SchemaMismatchError):
        build_model_input(_valid_customer(), bad_metadata)


def test_build_model_input_raises_on_unsupported_declared_feature() -> None:
    metadata = load_metadata()
    bad_metadata = _replace_schema(
        metadata,
        feature_names=(*metadata.input_schema.feature_names, "UnsupportedFeature"),
        dtypes={**metadata.input_schema.dtypes, "UnsupportedFeature": "int64"},
    )

    with pytest.raises(SchemaMismatchError):
        build_model_input(_valid_customer(), bad_metadata)


def test_build_model_input_raises_on_unsupported_dtype() -> None:
    metadata = load_metadata()
    bad_metadata = _replace_schema(
        metadata,
        dtypes={**metadata.input_schema.dtypes, "ProductsGroup": "object"},
    )

    with pytest.raises(SchemaMismatchError):
        build_model_input(_valid_customer(), bad_metadata)


def test_build_model_input_raises_on_unexpected_dtype_entry() -> None:
    metadata = load_metadata()
    bad_metadata = _replace_schema(
        metadata,
        dtypes={**metadata.input_schema.dtypes, "UnexpectedDtype": "int64"},
    )

    with pytest.raises(SchemaMismatchError):
        build_model_input(_valid_customer(), bad_metadata)


def _valid_customer() -> CustomerInput:
    return CustomerInput(
        credit_score=650,
        geography="France",
        gender="Female",
        age=40,
        tenure=3,
        balance=1200.0,
        num_of_products=2,
        has_cr_card=1,
        is_active_member=1,
        estimated_salary=90000.0,
    )


def _replace_schema(
    metadata: ArtifactMetadata,
    *,
    feature_names: tuple[str, ...] | None = None,
    dtypes: dict[str, str] | None = None,
) -> ArtifactMetadata:
    final_feature_names = feature_names or metadata.input_schema.feature_names
    final_dtypes: dict[str, str] = dict(dtypes or metadata.input_schema.dtypes)
    return replace(
        metadata,
        input_schema=InputSchemaMetadata(
            feature_names=final_feature_names,
            feature_count=len(final_feature_names),
            dtypes=final_dtypes,
        ),
    )
