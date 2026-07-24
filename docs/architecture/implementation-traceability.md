# Architecture Implementation Traceability

This document maps the approved architecture responsibilities to the physical
scaffold created during Prompt 2. It distinguishes structural materialization
from behavior intentionally deferred to later implementation stages.

| Architectural Responsibility | Physical Artifact | Current Stage | Notes |
|---|---|---|---|
| Application composition | `app.py` | Scaffolded | Neutral Streamlit entry point only; no business behavior implemented |
| Configuration | `src/churn_app/config.py` | Scaffolded | Repository-controlled paths only; no artifact loading |
| Domain representation | `src/churn_app/domain/` | Scaffolded | Infrastructure-independent contracts for customer input, model outputs, and risk levels |
| Artifact management | `src/churn_app/services/artifact_loader.py` | Contract only | Metadata parsing, joblib loading, hash verification, and error handling deferred |
| Input construction | `src/churn_app/services/input_builder.py` | Implemented | Validates `CustomerInput`, derives `ProductsGroup`, and builds one-row pandas DataFrames in metadata schema order |
| Prediction | `src/churn_app/services/prediction_service.py` | Contract only | Pipeline execution, probability extraction, and result normalization deferred |
| Orchestration | `src/churn_app/services/decision_policy.py` | Contract only | Four-level policy implementation deferred |
| Presentation | `src/churn_app/ui/` | Contract only | Final form, result rendering, recommendations, and disclaimer deferred |
| Test structure | `tests/` | Scaffolded | Structural tests only; behavior tests deferred until behavior exists |

## Dependency Direction

```text
app.py
  -> UI
  -> Services
  -> Domain

UI
  -> Domain
  -> Service contracts

Services
  -> Domain
  -> Configuration where required

Domain
  -> Python standard library only
```

## Deferred Behavior

- complete Streamlit UI;
- final customer form;
- artifact deserialization;
- hash verification;
- pipeline execution;
- probability extraction;
- four-level decision mapping;
- model-disagreement interpretation;
- operational recommendations;
- final disclaimer text;
- reference prediction reproduction;
- runtime caching.

## Input Construction Evidence

- `ProductsGroup` derivation is implemented in
  `src/churn_app/services/input_builder.py`.
- The derivation is based on the matching transformations in
  `notebooks/03_machine_learning.ipynb` cell 9 and
  `notebooks/02_statistical_modeling.ipynb` cell 21:
  `1 -> "1"`, `2 -> "2"`, `3 -> "3+"`, `4 -> "3+"`.
- Final feature names, count, ordering, and dtypes are controlled by
  `artifacts/metadata.json` through the validated `ArtifactMetadata` contract.
- Category validation for `Geography` and `Gender` uses the training evidence
  approved for this academic project: `France`, `Germany`, `Spain`, `Female`,
  and `Male`.
