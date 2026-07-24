# AGENTS.md

## 1. Project Overview

This repository contains an academic Machine Learning application for predicting bank customer churn.

The application uses two trained scikit-learn pipelines:

- Gradient Boosting: primary model, selected for its overall predictive balance and generalization.
- Decision Tree: complementary sensitivity model, selected for its higher recall and ability to detect churn cases missed by the primary model.

The application must not reduce the two predictions to an unexplained binary OR rule. It must preserve the individual model outputs and consolidate them into an interpretable four-level risk policy.

## 2. Project Objective

Build a reliable and explainable Streamlit application that:

1. collects customer attributes;
2. validates the input;
3. derives the required model features;
4. executes both trained pipelines;
5. presents each model prediction separately;
6. applies the defined decision policy;
7. returns an interpretable churn risk level;
8. explains agreement or disagreement between the models;
9. provides a non-deterministic operational recommendation.

This is an academic decision-support application. It must not claim that a customer will certainly leave the bank.

## 3. Source of Truth

The following files are authoritative:

- `artifacts/metadata.json`
  - artifact names;
  - model versions;
  - expected input schema;
  - positive class;
  - decision policy;
  - validation metrics;
  - artifact hashes.

- `artifacts/reference_predictions.csv`
  - reference inputs and expected predictions;
  - used for integration testing.

- serialized `.joblib` pipelines
  - contain both preprocessing and trained estimators;
  - must be loaded as complete pipelines;
  - preprocessing must not be reimplemented manually.

When code, assumptions, and metadata disagree, stop and report the inconsistency instead of silently guessing.

## 4. Model Roles

### Gradient Boosting

Role: primary model.

The Gradient Boosting prediction has greater operational relevance because it demonstrated the best overall balance among the evaluated models.

### Decision Tree

Role: complementary sensitivity model.

The Decision Tree must not override the Gradient Boosting prediction. Its purpose is to identify additional churn-risk cases and expose disagreement between the classifiers.

## 5. Decision Policy

The application must implement exactly the following policy:

| Gradient Boosting | Decision Tree | Risk level |
|-------------------|---------------|------------|
| 0                 | 0             | LOW        |
| 0                 | 1             | ATTENTION  |
| 1                 | 0             | HIGH       |
| 1                 | 1             | CRITICAL   |

Semantics:

- `LOW`: neither model detected sufficient evidence of churn;
- `ATTENTION`: only the more sensitive Decision Tree predicted churn;
- `HIGH`: the primary Gradient Boosting model predicted churn;
- `CRITICAL`: both models predicted churn.

The policy must be implemented in a pure, independently tested function.

Do not replace this policy with:

- majority voting;
- direct logical OR as the final binary result;
- arithmetic mean of probabilities;
- weighted average of probabilities;
- an invented combined probability.

Any change to the decision policy requires explicit user approval.

## 6. Probability Handling

If the pipelines expose `predict_proba`, show each probability separately.

Allowed:

- Gradient Boosting churn probability;
- Decision Tree churn probability.

Not allowed:

- averaging the probabilities;
- summing the probabilities;
- presenting a combined churn probability;
- describing uncalibrated probabilities as certainty.

Use language such as:

- estimated risk;
- model prediction;
- probability estimated by the model;
- indication of churn.

Avoid language such as:

- the customer will leave;
- guaranteed churn;
- certain prediction.

## 7. Input Contract

The application must accept user-friendly customer inputs and construct a pandas DataFrame compatible with the pipeline input schema declared in `metadata.json`.

The expected business inputs include:

- `CreditScore`;
- `Geography`;
- `Gender`;
- `Age`;
- `Tenure`;
- `Balance`;
- `NumOfProducts`;
- `HasCrCard`;
- `IsActiveMember`;
- `EstimatedSalary`.

The derived feature `ProductsGroup` must be calculated internally from `NumOfProducts`.

The user must not be asked to provide both `NumOfProducts` and `ProductsGroup`.

Before prediction:

1. validate required fields;
2. derive `ProductsGroup`;
3. construct a one-row DataFrame;
4. align columns with the metadata schema;
5. reject missing or unexpected fields;
6. preserve expected data types.

Do not silently substitute default values for missing mandatory inputs.

## 8. Feature Derivation

Implement product grouping in a dedicated function.

The implementation must reproduce exactly the transformation used during training.

Do not infer or change category labels from intuition.

If the training transformation cannot be verified from the repository or metadata, stop and request clarification.

## 9. Architecture Rules

Maintain separation between:

- user interface;
- input validation;
- feature construction;
- artifact loading;
- model inference;
- decision policy;
- result presentation.

Recommended responsibilities:

- `app.py`: Streamlit composition only;
- `src/churn_app/config.py`: repository paths and application configuration;
- `src/churn_app/domain/`: immutable domain models and enums;
- `src/churn_app/services/artifact_loader.py`: loading and artifact integrity;
- `src/churn_app/services/input_builder.py`: validation and DataFrame construction;
- `src/churn_app/services/prediction_service.py`: execution of both pipelines;
- `src/churn_app/services/decision_policy.py`: risk consolidation;
- `src/churn_app/ui/`: Streamlit components.

Do not place model-loading logic, business rules, and UI rendering in the same function.

Prefer small, typed, deterministic functions.

## 10. Artifact Loading

Load artifacts only from the configured artifacts directory.

Requirements:

- use `joblib`;
- load each model once per application process;
- use Streamlit resource caching where appropriate;
- provide clear errors when an artifact is missing or incompatible;
- never download or replace models automatically;
- never retrain models inside the application;
- never modify serialized artifacts at runtime.

Only trusted local model files may be loaded.

If SHA-256 hashes exist in `metadata.json`, provide a validation function and test it.

## 11. Error Handling

The application must fail safely and informatively.

Handle at minimum:

- missing artifact;
- invalid metadata;
- schema mismatch;
- unsupported input category;
- incompatible artifact;
- model without `predict`;
- model without `predict_proba`;
- malformed reference data;
- unexpected prediction output.

Do not expose raw stack traces to the Streamlit user interface.

Developer-facing exceptions should preserve useful context and exception chaining.

## 12. User Interface Requirements

Use Streamlit.

The interface must include:

1. title and short academic context;
2. customer input form;
3. explicit prediction action;
4. consolidated risk level;
5. individual model results;
6. individual probabilities when available;
7. explanation of model agreement or disagreement;
8. operational recommendation;
9. disclaimer that the output supports analysis and is not a deterministic decision.

The interface should be clear and professional, but avoid unnecessary animation, excessive styling, or visual complexity.

Do not use color as the only way to communicate risk.

Each risk level must also include textual identification.

## 13. Validation Rules

Apply domain-compatible validation without inventing unsupported business assumptions.

At minimum:

- numeric fields must be finite;
- `CreditScore` must be positive;
- `Age` must be positive;
- `Tenure` must not be negative;
- `Balance` must not be negative;
- `NumOfProducts` must be a positive integer;
- `EstimatedSalary` must not be negative;
- binary fields must use only allowed values;
- categorical fields must use categories supported by the trained pipeline.

Do not impose arbitrary upper bounds unless they are derived from the dataset, metadata, or explicit project requirements.

Supported categorical values must be implemented in the input validation layer using the categories observed during model training:

- `Geography`: `France`, `Germany`, `Spain`;
- `Gender`: `Female`, `Male`;
- `ProductsGroup`: `1`, `2`, `3+`.

Do not extend `metadata.json` to declare categorical domains in this academic project.

## 14. Testing Requirements

Use `pytest`.

Every implementation task must preserve or add tests.

Minimum required coverage:

### Unit tests

- all four decision-policy combinations;
- product-group derivation;
- input validation;
- DataFrame construction;
- schema ordering;
- interpretation text selection.

### Integration tests

- both artifacts load successfully;
- both models generate predictions;
- probabilities are in the interval `[0, 1]`;
- output classes are valid;
- reference cases reproduce expected predictions;
- serialized model hashes match metadata when hashes are available.

Tests must not retrain the models.

## 15. Reference Prediction Tests

Use `artifacts/reference_predictions.csv` as the main integration contract.

For every reference row:

1. extract the feature columns;
2. execute both pipelines;
3. compare predicted classes exactly;
4. compare probabilities using an appropriate floating-point tolerance;
5. verify the resulting decision-policy category.

If a reference case fails, report the discrepancy. Do not update the expected outputs automatically.

## 16. Code Quality

Use:

- Python type hints;
- descriptive names;
- docstrings for public modules, classes, and functions;
- `pathlib.Path`;
- explicit exception types;
- pure functions for deterministic business logic;
- enums for risk levels where useful.

Avoid:

- broad `except Exception` without re-raising or context;
- duplicated schema definitions;
- global mutable state;
- hard-coded artifact paths throughout the code;
- unexplained numeric constants;
- dead code;
- premature abstractions;
- unnecessary classes.

Code and identifiers must be written in English.

The user-facing interface may be written in Portuguese.

## 17. Dependency Management

Use `uv` and `pyproject.toml`.

Keep dependencies minimal.

Expected runtime dependencies:

- streamlit;
- pandas;
- numpy;
- scikit-learn;
- joblib.

Expected development dependencies:

- pytest;
- ruff;
- mypy, only if configured and used consistently.

Do not add a dependency when the same requirement can be reasonably implemented with the Python standard library.

## 18. Commands

Use the commands defined by the repository configuration.

Expected commands:

```bash
uv sync
uv run streamlit run app.py
uv run pytest
uv run ruff check .
uv run ruff format --check .
```

Before completing a coding task, run all available relevant checks.

If a command cannot be executed, state:

which command failed;
why it failed;
what remains unverified.

Do not claim that tests passed unless they were actually executed successfully.

## 19. Change Discipline

Before editing:

inspect the repository;
read metadata.json;
inspect the input schema;
inspect the reference cases;
identify existing tests and conventions;
propose the smallest coherent implementation.

During editing:

avoid unrelated refactoring;
preserve working behavior;
keep the patch focused;
update tests with behavior changes;
update documentation when architecture or commands change.

After editing:

run tests;
run linting;
inspect the final diff;
confirm no artifact was overwritten;
summarize changes and validation evidence.

##  20. Security and Safety

Serialized joblib artifacts may execute code during deserialization.

Therefore:

load only repository-controlled artifacts;
never load user-uploaded model files;
never accept arbitrary artifact paths from the UI;
never deserialize remote content;
do not suppress compatibility warnings without justification.

Do not store customer input persistently.

Do not add telemetry, analytics, external APIs, or network calls unless explicitly requested.

## 21. Definition of Done

A task is complete only when:

requested behavior is implemented;
architecture boundaries remain respected;
tests cover the new behavior;
reference predictions remain valid;
relevant tests and quality checks pass;
no model artifact has been modified;
user-facing messages remain non-deterministic and academically appropriate;
documentation is updated where necessary.
## 22. Agent Response Format

At the end of each coding task, report:

Implemented

Brief summary of changes.

Files changed

List the relevant files.

Validation

Commands executed and their results.

Remaining risks

Only unresolved or unverified items.

Do not provide generic success claims.
Do not hide failed tests or skipped validation.
