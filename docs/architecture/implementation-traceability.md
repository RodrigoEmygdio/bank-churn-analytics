# Architecture Implementation Traceability

This document maps the approved architecture responsibilities to the physical
scaffold created during Prompt 2. It distinguishes structural materialization
from behavior intentionally deferred to later implementation stages.

| Architectural Responsibility | Physical Artifact                                 | Current Stage | Notes                                                                                                                                                                       |
|------------------------------|---------------------------------------------------|---------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Application composition      | `app.py`                                          | Implemented   | Streamlit entry point delegates submitted customer data through the approved service pipeline without business-rule implementation                                          |
| Configuration                | `src/churn_app/config.py`                         | Scaffolded    | Repository-controlled paths only; no artifact loading                                                                                                                       |
| Domain representation        | `src/churn_app/domain/`                           | Implemented   | Immutable infrastructure-independent contracts for customer input, model identity, independent predictions, and risk levels                                                 |
| Artifact management          | `src/churn_app/services/artifact_loader.py`       | Implemented   | Metadata parsing, repository validation, hash verification, joblib loading, and deterministic artifact exceptions                                                           |
| Input construction           | `src/churn_app/services/input_builder.py`         | Implemented   | Validates `CustomerInput`, derives `ProductsGroup`, and builds one-row pandas DataFrames in metadata schema order                                                           |
| Prediction                   | `src/churn_app/services/prediction_service.py`    | Implemented   | Executes both loaded pipelines independently, extracts model-specific probabilities when available, and returns immutable prediction contracts                              |
| Decision Policy              | `src/churn_app/services/decision_policy.py`       | Implemented   | Pure infrastructure-independent mapping from four predicted-class combinations to `RiskLevel`; probabilities are not used                                                   |
| Risk Interpreter             | `src/churn_app/services/risk_interpreter.py`      | Implemented   | Pure infrastructure-independent explanation of a supplied `PredictionResult` and `RiskLevel`; validates consistency without recalculating risk                              |
| Recommendation Engine        | `src/churn_app/services/recommendation_engine.py` | Implemented   | Pure business-domain mapping from interpreted `RiskLevel` to immutable recommendation contracts; presentation remains deferred                                              |
| Presentation Layer           | `src/churn_app/services/presentation_layer.py`    | Implemented   | Pure contract composition from prediction, interpretation, and recommendation results into immutable `PresentationResult`; includes independent model presentation evidence |
| Streamlit UI                 | `src/churn_app/ui/`                               | Implemented   | Native wide two-panel layout with compact form, result panel, model probability presentation, collapsible analytical details, and native visual risk treatment              |
| UI internationalization      | `src/churn_app/i18n/`                             | Implemented   | Central deterministic translation catalog, explicit `Locale` contract, bilingual form/result rendering, and canonical domain-value preservation beneath localized labels    |
| Test structure               | `tests/`                                          | Implemented   | Unit, integration, artifact-contract, and architectural-boundary tests cover implemented behavior                                                                           |

## Dependency Direction

```text
app.py
  -> UI
  -> Services
  -> Domain

UI
  -> Domain
  -> Service contracts
  -> i18n

Services
  -> Domain
  -> Configuration where required

Domain
  -> Python standard library only
```

## Deferred Behavior

- reference prediction reproduction;
- runtime caching;
- deployment;
- authentication.

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
