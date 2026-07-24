# Repository Diagnosis

- Status: Validated
- Diagnosis date: 2026-07-24
- Formalization date: 2026-07-24
- Scope: Churn prediction application

## 1. Purpose

This document records the validated repository state before Streamlit application implementation. It formalizes the reviewed diagnosis, the repository alignment decisions already approved by the user, and the current evidence available in the repository.

It is not an implementation plan for code generation. It is a factual baseline for future architecture and implementation work.

## 2. Inspection Scope

Prompt 1 inspection covered:

- `AGENTS.md`;
- `README.md`;
- `pyproject.toml`;
- `uv.lock`;
- `artifacts/`;
- `artifacts/metadata.json`;
- `artifacts/reference_predictions.csv`;
- exported `.joblib` model pipelines;
- `notebooks/`;
- `data/raw/Churn_Modelling.csv`;
- `docs/`;
- existing source-code directories;
- existing tests.

The formalization pass also checked that the architecture documents did not already exist.

## 3. Confirmed Repository State

- The repository is an academic Machine Learning project for bank customer churn risk analysis.
- `AGENTS.md` is present and remains the authoritative project instruction file.
- The approved application direction is Streamlit.
- The approved application package structure is `app.py` plus `src/churn_app/...`.
- The repository currently contains no application implementation scaffold: `app.py`, `src/`, and `tests/` are absent.
- Obsolete empty directories from the prior direction (`api/`, `models/`, `frontend/`, `report/`) are absent after repository alignment.
- The repository contains trained local artifacts in `artifacts/`.
- The repository contains notebooks and scientific documentation from the modeling process.
- The project uses `uv`, `pyproject.toml`, and `uv.lock`.
- Runtime and development dependencies needed for the future Streamlit implementation are declared.

## 4. Existing Assets

Model artifacts:

- `artifacts/gradient_boosting_pipeline.joblib`;
- `artifacts/decision_tree_pipeline.joblib`.

Metadata:

- `artifacts/metadata.json`.

Reference predictions:

- `artifacts/reference_predictions.csv`.

Notebooks:

- `notebooks/01_eda.ipynb`;
- `notebooks/02_statistical_modeling.ipynb`;
- `notebooks/03_machine_learning.ipynb`.

Source code:

- No application source code exists yet.

Tests:

- No test directory exists yet.

Dependency configuration:

- `pyproject.toml`;
- `uv.lock`;
- `.python-version`.

Documentation:

- `README.md`;
- `AGENTS.md`;
- `docs/Relatorio.md`;
- `docs/img*.png`;
- `docs/tables/*.md`;
- `docs/review.md`.

## 5. Missing Assets

The following approved implementation assets are intentionally not present yet:

- `app.py`;
- `src/churn_app/__init__.py`;
- `src/churn_app/config.py`;
- `src/churn_app/domain/__init__.py`;
- `src/churn_app/domain/customer.py`;
- `src/churn_app/domain/prediction.py`;
- `src/churn_app/domain/risk_level.py`;
- `src/churn_app/services/__init__.py`;
- `src/churn_app/services/artifact_loader.py`;
- `src/churn_app/services/input_builder.py`;
- `src/churn_app/services/prediction_service.py`;
- `src/churn_app/services/decision_policy.py`;
- `src/churn_app/ui/__init__.py`;
- `src/churn_app/ui/form.py`;
- `src/churn_app/ui/result.py`;
- `tests/unit/test_input_builder.py`;
- `tests/unit/test_decision_policy.py`;
- `tests/integration/test_artifact_loading.py`;
- `tests/integration/test_reference_predictions.py`.

These files must not be treated as missing by accident. They are future implementation work.

## 6. Artifact Inventory

`gradient_boosting_pipeline.joblib`

- Filename: `artifacts/gradient_boosting_pipeline.joblib`
- Role: primary model
- Format: compressed joblib serialized scikit-learn pipeline
- Integrity information: SHA-256 in metadata and verified during diagnosis as `98a0977172722299c88d251274b9661ebeadf37b1e19bbed2e5101400195b357`
- Relevant version data: artifact version `1.0.0`; scikit-learn `1.9.0`; Python `3.14.3`; pandas `3.0.3`; numpy `2.5.1`; joblib `1.5.3`
- Runtime responsibility: execute the primary churn prediction using the complete serialized pipeline.

`decision_tree_pipeline.joblib`

- Filename: `artifacts/decision_tree_pipeline.joblib`
- Role: complementary sensitivity model
- Format: compressed joblib serialized scikit-learn pipeline
- Integrity information: SHA-256 in metadata and verified during diagnosis as `246893e871742fea9629afb8543eab2ce6d2117be6c0810160f070cc89e9dbd3`
- Relevant version data: artifact version `1.0.0`; scikit-learn `1.9.0`; Python `3.14.3`; pandas `3.0.3`; numpy `2.5.1`; joblib `1.5.3`
- Runtime responsibility: execute the complementary sensitivity prediction using the complete serialized pipeline.

`metadata.json`

- Filename: `artifacts/metadata.json`
- Role: runtime and integration contract for artifacts, schema, positive class, policy, metrics, and hashes
- Format: JSON
- Integrity information: repository file hash observed during alignment as `b8d2e7d2b10337641316da7f44b4c727c481b993131294dd5225d0db670169df`
- Relevant version data: artifact version `1.0.0`; exported at `2026-07-24T07:52:44.689492+00:00`
- Runtime responsibility: define artifact filenames, expected input schema, positive class, model roles, decision policy, validation metrics, and artifact hashes.

`reference_predictions.csv`

- Filename: `artifacts/reference_predictions.csv`
- Role: integration contract
- Format: CSV
- Integrity information: repository file hash observed during alignment as `a00362094bf14fe88ee37df67150ce78b1a1d36d90bd1adbe417e3cd6eee4a84`
- Relevant version data: generated with artifact version `1.0.0` context
- Runtime responsibility: none in production UI; used by tests to verify artifact loading, predictions, probabilities, and risk-policy mapping.

## 7. Input Contract

Expected feature names, in order:

1. `CreditScore`
2. `Geography`
3. `Gender`
4. `Age`
5. `Tenure`
6. `Balance`
7. `NumOfProducts`
8. `HasCrCard`
9. `IsActiveMember`
10. `EstimatedSalary`
11. `ProductsGroup`

Expected data types from `metadata.json`:

- `CreditScore`: `int64`
- `Geography`: `str`
- `Gender`: `str`
- `Age`: `int64`
- `Tenure`: `int64`
- `Balance`: `float64`
- `NumOfProducts`: `int64`
- `HasCrCard`: `int64`
- `IsActiveMember`: `int64`
- `EstimatedSalary`: `float64`
- `ProductsGroup`: `category`

Allowed categorical values confirmed by training evidence and approved user correction:

- `Geography`: `France`, `Germany`, `Spain`
- `Gender`: `Female`, `Male`
- `ProductsGroup`: `1`, `2`, `3+`

Derived features:

- `ProductsGroup` must be derived internally from `NumOfProducts`.
- The user must not be asked to provide `ProductsGroup`.
- The training transformation is:
  - `1` -> `1`
  - `2` -> `2`
  - `3` -> `3+`
  - `4` -> `3+`

Schema ordering requirements:

- The prediction DataFrame must align exactly with `metadata.json` `input_schema.feature_names`.
- Missing required fields must be rejected.
- Unexpected user input fields must be rejected.
- Data types must be preserved according to the metadata contract.

Unresolved schema details:

- Metadata intentionally does not declare categorical domains.
- Categorical validation must remain in the input validation layer for this academic project.
- No arbitrary upper bounds are approved for numeric fields.

## 8. Output Contract

Prediction classes:

- The positive class is `1`.
- Valid prediction classes are `0` and `1`.

Probability outputs:

- If exposed by the pipelines, Gradient Boosting churn probability must be shown separately.
- If exposed by the pipelines, Decision Tree churn probability must be shown separately.
- No averaged, summed, weighted, or combined churn probability may be presented.

Risk levels:

| Gradient Boosting | Decision Tree | Risk level |
|-------------------|---------------|------------|
| 0                 | 0             | LOW        |
| 0                 | 1             | ATTENTION  |
| 1                 | 0             | HIGH       |
| 1                 | 1             | CRITICAL   |

Interpretation requirements:

- Individual model outputs must be preserved.
- Model agreement and disagreement must be explained.
- Gradient Boosting remains the primary model.
- Decision Tree remains the complementary sensitivity model and must not override Gradient Boosting.

Operational recommendation boundaries:

- Recommendations must be non-deterministic.
- User-facing language must not claim that a customer will certainly leave the bank.
- The output supports analysis and must not be framed as an automatic decision.

## 9. Validated Architectural Conclusions

- The application will be a modular in-process Streamlit application.
- No separate prediction API is part of the approved baseline.
- The approved package layout is `app.py` plus `src/churn_app/...`.
- Complete local joblib pipelines must be loaded; preprocessing must not be reimplemented.
- `metadata.json` is the runtime contract for artifact names, schema, positive class, policy, metrics, and hashes.
- `reference_predictions.csv` is the integration testing contract.
- Gradient Boosting is the primary model.
- Decision Tree is the complementary sensitivity model.
- The four-level decision policy is mandatory.
- Probabilities, when available, must remain model-specific.
- Runtime retraining is forbidden.
- Serialized artifacts must not be modified.
- `metadata.json` must not be extended with categorical domains in this academic project.

## 10. Constraints

Constraints from `AGENTS.md`:

- Use Streamlit.
- Preserve architectural separation among UI, validation, feature construction, artifact loading, inference, decision policy, and presentation.
- Implement the decision policy in a pure independently tested function.
- Use `pytest`.
- Use `uv` and `pyproject.toml`.
- Use `joblib` to load local artifacts.
- Load only repository-controlled artifacts.
- Do not retrain, download, replace, or modify model artifacts at runtime.
- Do not expose raw stack traces in the Streamlit UI.
- Do not store customer input persistently.
- Do not add telemetry, analytics, external APIs, or network calls unless explicitly requested.

Constraints from artifacts and metadata:

- Expected feature count is 11.
- Positive class is `1`.
- Model artifact filenames are fixed by metadata.
- Artifact hashes are present and must be validated.
- Decision policy keys and risk labels are fixed by metadata.

Constraints from approved corrections:

- Documentation for research/scientific context should remain in Portuguese.
- Internal code artifacts may remain in English.
- Notebook dependencies must be preserved.
- Categorical domains are validation-layer knowledge from training evidence, not metadata extensions.

## 11. Technical Risks

### Confirmed Risks

- No application source code exists yet.
- No tests exist yet.
- The implementation must introduce test coverage from scratch.
- `metadata.json` does not explicitly declare categorical domains by design.
- Joblib deserialization is inherently sensitive and must remain limited to trusted local artifacts.
- The reference predictions must not be updated automatically if tests fail.

### Conditional Risks

- Pipeline compatibility may fail if runtime Python or library versions differ materially from metadata versions.
- A model may not expose `predict_proba`; the UI must handle that case if encountered.
- Unsupported categories may be accepted accidentally if validation is incomplete.
- Schema ordering bugs may occur if DataFrame construction duplicates schema definitions instead of deriving from metadata.
- Hidden preprocessing assumptions may be violated if implementation reimplements preprocessing outside the serialized pipelines.

## 12. Open Questions

Question: Should unused research/API dependencies be removed later?

- Why it matters: dependency scope affects install time and maintenance.
- Expected source of truth: explicit user approval after notebook needs are reassessed.
- Implementation blocked: no.

Question: Should user-facing Streamlit text be Portuguese, English, or bilingual?

- Why it matters: the academic audience is Brazilian, while internal identifiers are English.
- Expected source of truth: explicit user approval before UI writing.
- Implementation blocked: partially; UI copy should not be finalized without this decision.

Question: Should future production metadata include categorical domains?

- Why it matters: metadata-owned domains improve portability and reduce duplicated validation knowledge.
- Expected source of truth: future production-oriented ADR or metadata versioning decision.
- Implementation blocked: no. Current scope explicitly keeps categorical domains in validation logic.

Question: Should probability calibration be evaluated?

- Why it matters: uncalibrated probabilities must not be described as certainty.
- Expected source of truth: future modeling or calibration analysis.
- Implementation blocked: no.

## 13. Approved Implementation Sequence

1. Align dependencies and tooling for Streamlit, pytest, and Ruff while preserving notebook dependencies.
2. Implement domain primitives and the pure decision policy with unit tests.
3. Implement metadata loading and artifact integrity checks.
4. Implement `ProductsGroup` derivation.
5. Implement input validation and one-row DataFrame construction.
6. Implement local model loading.
7. Implement prediction result normalization.
8. Implement interpretation and recommendation text selection.
9. Build Streamlit UI composition.
10. Add reference prediction integration tests.
11. Align documentation with implemented behavior when implementation is complete.
12. Run final validation checks and inspect the final diff.

## 14. First Approved Implementation Task

The smallest testable next task is to implement domain primitives and the pure decision-policy function with tests for all four Gradient Boosting and Decision Tree combinations.

This task is preferred because it does not require deserializing artifacts, does not modify artifacts, and locks down the core business policy before UI or inference code is added.

## 15. Traceability

This document was created from:

- `AGENTS.md` as the highest-priority source of truth;
- the current repository state on 2026-07-24;
- the reviewed Prompt 1 diagnosis recorded in the conversation;
- the user-approved corrections establishing the `src/churn_app` structure, Portuguese academic documentation, preserved notebook dependencies, removal of obsolete empty directories, and validation-layer categorical domains;
- repository alignment already applied before this formalization.
