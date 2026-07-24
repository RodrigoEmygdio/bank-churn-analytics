"""Input validation and model-ready feature construction.

This module owns the boundary from `CustomerInput` to a single-row pandas
DataFrame compatible with the metadata-declared model schema. It does not load
metadata, load artifacts, execute models, or render UI.
"""

from __future__ import annotations

import math

import pandas as pd

from churn_app.domain import CustomerInput
from churn_app.services.artifact_loader import ArtifactMetadata

SUPPORTED_GEOGRAPHIES = frozenset({"France", "Germany", "Spain"})
SUPPORTED_GENDERS = frozenset({"Female", "Male"})
PRODUCTS_GROUP_CATEGORIES = ("1", "2", "3+")

_DOMAIN_TO_FEATURE = {
    "credit_score": "CreditScore",
    "geography": "Geography",
    "gender": "Gender",
    "age": "Age",
    "tenure": "Tenure",
    "balance": "Balance",
    "num_of_products": "NumOfProducts",
    "has_cr_card": "HasCrCard",
    "is_active_member": "IsActiveMember",
    "estimated_salary": "EstimatedSalary",
}


class InputValidationError(ValueError):
    """Base exception for deterministic input-boundary failures."""


class InvalidFieldValueError(InputValidationError):
    """Raised when a field has an invalid type or structurally invalid value."""

    def __init__(self, field: str, value: object, reason: str) -> None:
        self.field = field
        self.value = value
        self.reason = reason
        super().__init__(f"Invalid value for {field}: {value!r}. Reason: {reason}")


class UnsupportedCategoryError(InvalidFieldValueError):
    """Raised when a categorical field is outside the training evidence."""


class FeatureConstructionError(InputValidationError):
    """Raised when a derived feature cannot be constructed."""


class SchemaMismatchError(InputValidationError):
    """Raised when constructed features do not match metadata schema."""


def build_inference_input(
    customer: CustomerInput, metadata: ArtifactMetadata
) -> pd.DataFrame:
    """Build one model-ready row in the metadata-declared feature order."""
    return build_model_input(customer, metadata)


def build_model_input(
    customer: CustomerInput, metadata: ArtifactMetadata
) -> pd.DataFrame:
    """Validate customer data and construct a model-ready single-row DataFrame."""
    validate_customer_input(customer)
    row = _build_feature_row(customer)
    _verify_schema_keys(row, metadata)

    frame = pd.DataFrame(
        [{feature: row[feature] for feature in metadata.input_schema.feature_names}]
    )
    _apply_metadata_dtypes(frame, metadata)
    _verify_dataframe_contract(frame, metadata)
    return frame


def validate_customer_input(customer: CustomerInput) -> None:
    """Validate user-provided customer fields before feature construction."""
    _validate_positive_int("credit_score", customer.credit_score)
    _validate_category("geography", customer.geography, SUPPORTED_GEOGRAPHIES)
    _validate_category("gender", customer.gender, SUPPORTED_GENDERS)
    _validate_positive_int("age", customer.age)
    _validate_non_negative_int("tenure", customer.tenure)
    _validate_non_negative_float("balance", customer.balance)
    _validate_positive_int("num_of_products", customer.num_of_products)
    _validate_binary_int("has_cr_card", customer.has_cr_card)
    _validate_binary_int("is_active_member", customer.is_active_member)
    _validate_non_negative_float("estimated_salary", customer.estimated_salary)


def derive_products_group(num_of_products: int) -> str:
    """Derive ProductsGroup using the training-time notebook transformation.

    Evidence: `notebooks/03_machine_learning.ipynb`, cell 9, and
    `notebooks/02_statistical_modeling.ipynb`, cell 21, map 1 to "1",
    2 to "2", and 3 or 4 to "3+".
    """
    _validate_positive_int("num_of_products", num_of_products)
    if num_of_products == 1:
        return "1"
    if num_of_products == 2:
        return "2"
    if num_of_products in {3, 4}:
        return "3+"
    raise FeatureConstructionError(
        "ProductsGroup can only be derived from NumOfProducts values observed "
        f"during training: 1, 2, 3, or 4. Got {num_of_products!r}."
    )


def _build_feature_row(customer: CustomerInput) -> dict[str, object]:
    row = {
        feature_name: getattr(customer, attribute_name)
        for attribute_name, feature_name in _DOMAIN_TO_FEATURE.items()
    }
    row["ProductsGroup"] = derive_products_group(customer.num_of_products)
    return row


def _verify_schema_keys(row: dict[str, object], metadata: ArtifactMetadata) -> None:
    declared_features = tuple(metadata.input_schema.feature_names)
    actual_features = tuple(row.keys())
    if len(declared_features) != metadata.input_schema.feature_count:
        raise SchemaMismatchError(
            "metadata.input_schema.feature_count does not match feature_names."
        )

    missing_features = set(declared_features) - row.keys()
    extra_features = row.keys() - set(declared_features)
    if missing_features or extra_features:
        raise SchemaMismatchError(
            "Constructed features do not match metadata schema: "
            f"missing={sorted(missing_features)}, extra={sorted(extra_features)}"
        )

    unsupported_features = (
        set(declared_features) - set(_DOMAIN_TO_FEATURE.values()) - {"ProductsGroup"}
    )
    if unsupported_features:
        raise SchemaMismatchError(
            f"Metadata declares unsupported features: {sorted(unsupported_features)}"
        )

    if len(actual_features) != len(row):
        raise SchemaMismatchError("Constructed feature names must be unique.")


def _apply_metadata_dtypes(frame: pd.DataFrame, metadata: ArtifactMetadata) -> None:
    for feature_name in metadata.input_schema.feature_names:
        expected_dtype = metadata.input_schema.dtypes.get(feature_name)
        if expected_dtype is None:
            raise SchemaMismatchError(
                f"Missing dtype for declared feature {feature_name}."
            )

        try:
            if expected_dtype == "int64":
                frame[feature_name] = frame[feature_name].astype("int64")
            elif expected_dtype == "float64":
                frame[feature_name] = frame[feature_name].astype("float64")
            elif expected_dtype == "str":
                frame[feature_name] = frame[feature_name].astype("string")
            elif expected_dtype == "category":
                frame[feature_name] = pd.Categorical(
                    frame[feature_name],
                    categories=PRODUCTS_GROUP_CATEGORIES,
                )
            else:
                raise SchemaMismatchError(
                    f"Unsupported metadata dtype for {feature_name}: {expected_dtype}"
                )
        except (TypeError, ValueError) as exc:
            raise SchemaMismatchError(
                f"Could not apply dtype {expected_dtype} to feature {feature_name}."
            ) from exc


def _verify_dataframe_contract(frame: pd.DataFrame, metadata: ArtifactMetadata) -> None:
    declared_features = list(metadata.input_schema.feature_names)
    actual_features = list(frame.columns)
    if actual_features != declared_features:
        raise SchemaMismatchError(
            f"DataFrame columns do not match metadata order: {actual_features}"
        )
    if frame.shape != (1, metadata.input_schema.feature_count):
        raise SchemaMismatchError(
            "DataFrame must contain exactly one row and metadata feature_count columns."
        )
    if metadata.target in frame.columns:
        raise SchemaMismatchError("DataFrame must not contain the target column.")

    dtype_features = set(metadata.input_schema.dtypes)
    column_features = set(frame.columns)
    if dtype_features != column_features:
        raise SchemaMismatchError(
            "Metadata dtypes must match DataFrame columns exactly: "
            f"missing={sorted(column_features - dtype_features)}, "
            f"unexpected={sorted(dtype_features - column_features)}"
        )

    for feature_name, expected_dtype in metadata.input_schema.dtypes.items():
        if expected_dtype == "category":
            if not isinstance(frame[feature_name].dtype, pd.CategoricalDtype):
                raise SchemaMismatchError(f"{feature_name} must be categorical.")
        elif expected_dtype == "str":
            if not (
                pd.api.types.is_string_dtype(frame[feature_name])
                or pd.api.types.is_object_dtype(frame[feature_name])
            ):
                raise SchemaMismatchError(f"{feature_name} must be string-like.")
        elif expected_dtype != str(frame[feature_name].dtype):
            raise SchemaMismatchError(
                f"{feature_name} dtype mismatch: expected {expected_dtype}, "
                f"got {frame[feature_name].dtype}"
            )


def _validate_category(
    field: str, value: object, supported_values: frozenset[str]
) -> None:
    if not isinstance(value, str):
        raise UnsupportedCategoryError(field, value, "value must be a string")
    if value not in supported_values:
        raise UnsupportedCategoryError(
            field,
            value,
            f"supported values are {sorted(supported_values)}",
        )


def _validate_binary_int(field: str, value: object) -> None:
    _validate_int(field, value)
    if value not in {0, 1}:
        raise InvalidFieldValueError(field, value, "value must be 0 or 1")


def _validate_positive_int(field: str, value: object) -> None:
    _validate_int(field, value)
    if value <= 0:
        raise InvalidFieldValueError(field, value, "value must be positive")


def _validate_non_negative_int(field: str, value: object) -> None:
    _validate_int(field, value)
    if value < 0:
        raise InvalidFieldValueError(field, value, "value must not be negative")


def _validate_int(field: str, value: object) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise InvalidFieldValueError(field, value, "value must be an integer")


def _validate_non_negative_float(field: str, value: object) -> None:
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise InvalidFieldValueError(field, value, "value must be numeric")
    if not math.isfinite(value):
        raise InvalidFieldValueError(field, value, "value must be finite")
    if value < 0:
        raise InvalidFieldValueError(field, value, "value must not be negative")
