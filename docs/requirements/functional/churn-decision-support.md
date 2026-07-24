# Functional Requirements — Churn Decision-Support Application

## 1. Purpose

This document defines what the bank-customer churn decision-support application
must do.

Implementation details, architectural boundaries, and quality attributes are
defined separately in ADRs, architecture documents, and non-functional
requirements.

## 2. Scope

The application analyzes customer attributes using two trained Machine Learning
pipelines and produces an interpretable churn-risk assessment.

The application supports analysis. It does not make an automatic retention
decision and must not claim certainty that a customer will leave the bank.

## 3. Actors

### Analyst or Application User

Provides customer attributes and requests an analysis.

### Application

Validates the input, derives required features, executes both models, applies
the approved policy, and presents an interpretable result.

## 4. Customer Input

The application must accept the following user-provided fields:

- `CreditScore`
- `Geography`
- `Gender`
- `Age`
- `Tenure`
- `Balance`
- `NumOfProducts`
- `HasCrCard`
- `IsActiveMember`
- `EstimatedSalary`

The user must not be asked to provide `ProductsGroup`.

## 5. Supported Categorical Values

The following categories are supported by the trained model contract:

### Geography

- `France`
- `Germany`
- `Spain`

### Gender

- `Female`
- `Male`

### Binary Fields

The following fields accept only `0` or `1`:

- `HasCrCard`
- `IsActiveMember`

The application must reject unsupported categories and invalid binary values.

## 6. Input Validation

Before inference, the application must validate all required fields.

At minimum:

- numeric fields must contain values of the expected numeric kind;
- numeric values must be finite;
- `CreditScore` must be a positive integer;
- `Age` must be a positive integer;
- `Tenure` must be a non-negative integer;
- `Balance` must be non-negative;
- `NumOfProducts` must be a positive integer supported by the approved feature derivation;
- `EstimatedSalary` must be non-negative;
- binary values must be exactly `0` or `1`;
- categorical values must belong to the supported model categories;
- missing required values must be rejected.

The application must not silently:

- substitute defaults for missing mandatory fields;
- clamp values;
- normalize unsupported spellings;
- coerce arbitrary strings into numbers;
- convert unsupported categories.

No arbitrary upper bound may be introduced without evidence from an approved
requirement or domain rule.

## 7. Derived Feature

The application must derive `ProductsGroup` internally from `NumOfProducts`.

Approved mapping:

| NumOfProducts | ProductsGroup |
|---:|:---|
| 1 | `1` |
| 2 | `2` |
| 3 | `3+` |
| 4 | `3+` |

Values outside the approved training-time mapping must be rejected rather than
assigned to an invented category.

## 8. Model Input Construction

After validation, the application must:

1. derive `ProductsGroup`;
2. construct exactly one tabular row;
3. include only model input features;
4. exclude the target column;
5. align feature names and order with the operational metadata;
6. preserve the expected semantic data types;
7. reject missing, unexpected, or unsupported schema entries.

## 9. Model Execution

The application must execute both trained pipelines independently:

- Gradient Boosting;
- Decision Tree.

The pipelines must be used as complete exported pipelines, including their
preprocessing.

The application must preserve the individual output of each model.

## 10. Individual Results

For each model, the application must present:

- predicted class;
- model identity or display name;
- model role;
- churn probability when `predict_proba` is available.

The application must not hide disagreement between the models.

## 11. Consolidated Risk Result

The application must consolidate the two predicted classes into one of four
risk levels:

- `LOW`
- `MODERATE`
- `HIGH`
- `CRITICAL`

The approved mapping is defined in
`docs/features/churn-risk-orchestration.md`.

No alternative aggregation rule may be introduced without explicit approval.

## 12. Probability Presentation

When probabilities are available, the application must show them separately:

- Gradient Boosting churn probability;
- Decision Tree churn probability.

The application must not:

- average probabilities;
- sum probabilities;
- calculate a combined probability;
- present uncalibrated probabilities as certainty.

## 13. Interpretation

The application must explain:

- whether the models agree;
- which model detected churn risk when they disagree;
- the operational meaning of the consolidated level.

Language must remain probabilistic and analytical.

Preferred expressions include:

- estimated risk;
- model prediction;
- probability estimated by the model;
- indication of churn risk.

Forbidden certainty claims include:

- the customer will leave;
- guaranteed churn;
- certain prediction.

## 14. Operational Recommendation

The application must provide a recommendation appropriate to the consolidated
risk level.

Recommendations must:

- support human analysis;
- avoid claiming an automatic or mandatory decision;
- remain distinguishable from the model prediction itself.

## 15. User Interface Behavior

The Streamlit interface must provide:

1. application title and short context;
2. customer input form;
3. explicit prediction action;
4. consolidated risk level;
5. individual model results;
6. individual probabilities when available;
7. agreement or disagreement explanation;
8. operational recommendation;
9. disclaimer that the result supports analysis and is not deterministic.

Risk must always be communicated textually. Color may support the message but
must not be the only communication channel.

## 16. Functional Error Behavior

The application must:

- prevent inference when input validation fails;
- provide an understandable message for invalid input;
- report that analysis cannot proceed when required artifacts or contracts are unavailable;
- avoid displaying raw stack traces to the user;
- avoid presenting partial predictions as a complete result.

## 17. Acceptance Criteria

The functional scope is satisfied when:

- a valid customer input produces one model-ready row;
- invalid input is rejected before model execution;
- `ProductsGroup` is derived internally;
- both pipelines are executed independently;
- individual predictions remain visible;
- each model probability remains separate;
- one approved risk level is produced;
- model disagreement is explicitly explained;
- the output contains a non-deterministic recommendation and disclaimer.
