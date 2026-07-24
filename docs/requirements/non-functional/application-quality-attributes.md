# Non-Functional Requirements — Application Quality Attributes

## 1. Purpose

This document defines the quality attributes and operational constraints of the
bank-customer churn decision-support application.

## 2. Reliability

The application must fail safely and deterministically.

It must:

- reject invalid metadata;
- reject incompatible input schemas;
- reject missing repository-controlled artifacts;
- reject artifact hash mismatches when hashes are declared;
- prevent model execution after validation failure;
- prevent partial artifact sets from being used;
- preserve useful developer-facing exception context;
- avoid exposing raw stack traces to end users.

Errors must use explicit exception types where practical.

## 3. Reproducibility

The application must preserve the behavior of the exported training artifacts.

It must:

- load complete serialized pipelines;
- avoid reimplementing model preprocessing manually;
- avoid retraining models inside the application;
- avoid modifying serialized artifacts at runtime;
- validate repository reference predictions;
- preserve feature names, order, count, and semantic dtypes;
- use deterministic feature derivation and decision policy functions.

Reference prediction failures must be reported. Expected outputs must not be
updated automatically.

## 4. Explainability and Responsible Communication

The application must preserve the contribution of both models.

It must:

- expose each model prediction separately;
- expose each available probability separately;
- explain model agreement or disagreement;
- communicate the role of each model;
- distinguish model output, interpretation, and recommendation;
- avoid presenting predictions as certainty;
- avoid inventing a combined churn probability.

The application is decision support, not an autonomous decision-maker.

## 5. Security

Serialized artifacts are executable content during deserialization.

Therefore, the application must:

- load only repository-controlled local artifacts;
- never deserialize remote content;
- never accept user-uploaded model files;
- never accept arbitrary artifact paths from the UI;
- never download or replace models automatically;
- avoid external APIs and network calls unless explicitly approved;
- avoid telemetry and analytics unless explicitly approved;
- avoid persistent storage of customer input.

## 6. Data Privacy

Customer input must remain transient.

The application must not:

- persist customer input;
- transmit customer input to external services;
- log sensitive input values by default;
- add analytics or tracking without explicit approval.

## 7. Maintainability

The implementation must preserve clear module responsibilities.

At minimum, separate:

- application composition;
- domain contracts;
- artifact loading and integrity;
- input validation;
- feature construction;
- inference;
- decision policy;
- interpretation;
- presentation.

Implementation should use:

- explicit typing;
- descriptive names;
- small functions;
- immutable domain contracts where practical;
- pure functions for deterministic rules;
- `pathlib.Path`;
- explicit exception types;
- minimal dependencies.

Implementation should avoid:

- global mutable state;
- duplicated schema definitions;
- broad silent exception handling;
- hard-coded artifact paths across modules;
- premature abstraction;
- dead code;
- unnecessary classes;
- hidden I/O during module import.

## 8. Testability

Deterministic business rules must be independently testable.

Required test categories include:

### Unit tests

- all decision-policy combinations;
- product-group derivation;
- customer input validation;
- DataFrame construction;
- schema ordering;
- interpretation selection.

### Integration tests

- repository artifacts load successfully;
- both pipelines can predict;
- probabilities, when available, are within `[0, 1]`;
- output classes are valid;
- reference cases reproduce expected predictions;
- declared artifact hashes match local files.

### Architectural boundary tests

Tests should protect approved dependency boundaries, including isolation of:

- domain from infrastructure libraries;
- artifact deserialization;
- pandas-based input construction;
- pure decision policy.

Tests must not retrain models.

## 9. Performance and Resource Use

The application must avoid unnecessary repeated model deserialization.

Repository-controlled model pipelines should be loaded once per application
process where compatible with the application architecture.

No strict latency, throughput, or memory targets are currently approved.

Agents must not invent numerical service-level targets.

## 10. Usability and Accessibility

The interface must be professional and understandable.

It must:

- use an explicit action to request prediction;
- identify risk with text;
- avoid using color as the only communication channel;
- avoid excessive animation or visual complexity;
- distinguish model evidence from operational recommendation;
- provide a clear non-deterministic disclaimer.

## 11. Compatibility

The application must use the versions and artifact contract recorded in
repository metadata and dependency configuration.

Incompatibility must produce a clear error rather than silent behavior changes.

## 12. Dependency Management

The project uses `uv` and `pyproject.toml`.

Runtime dependencies should remain minimal and may include:

- Streamlit;
- pandas;
- NumPy;
- scikit-learn;
- joblib.

Development dependencies may include:

- pytest;
- Ruff;
- mypy only when configured and used consistently.

Do not add a dependency when the standard library reasonably satisfies the
requirement.

## 13. Code Quality Verification

Relevant implementation work must be verified with the repository commands,
including where applicable:

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
```

A failed or unavailable command must be reported honestly.

## 14. Traceability

Feature rules derived from notebooks, reports, exports, or human decisions must
be traceable to their evidence.

Architecture implementation must remain linked to accepted ADRs and
implementation traceability.

## 15. Quality Acceptance Criteria

The application satisfies these quality requirements when:

- invalid states fail deterministically;
- model behavior is reproducible from repository artifacts;
- model outputs remain explainable and separate;
- no untrusted artifact can be loaded through the UI;
- customer input is not persisted or transmitted;
- architectural boundaries are protected by tests;
- relevant automated checks pass;
- remaining compatibility or verification risks are documented.
