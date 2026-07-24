# Feature Specification — Churn Risk Orchestration

## 1. Purpose

This feature coordinates customer input validation, model-ready feature
construction, independent model inference, risk consolidation, interpretation,
and operational recommendation.

It preserves the separate evidence produced by the Gradient Boosting and
Decision Tree pipelines.

## 2. Business Context

Customer churn analysis is treated as a decision-support problem.

The application must help an analyst identify different degrees of churn risk
without claiming certainty and without collapsing two models into an
unexplained binary rule.

## 3. Actors

### Analyst

Provides customer attributes and requests a churn-risk analysis.

### Churn Risk Orchestration

Coordinates the approved processing flow and returns a structured result.

## 4. Preconditions

Before orchestration:

- repository metadata must be valid;
- required artifact files must exist;
- declared artifact hashes must match when provided;
- both serialized pipelines must load successfully;
- customer input must satisfy the functional input contract.

## 5. User-Provided Inputs

The feature receives a `CustomerInput` containing:

- credit score;
- geography;
- gender;
- age;
- tenure;
- balance;
- number of products;
- credit-card indicator;
- active-member indicator;
- estimated salary.

The user does not provide `ProductsGroup`.

## 6. Derived Feature

`ProductsGroup` is derived from `NumOfProducts` using the exact transformation
used during model development:

| NumOfProducts | ProductsGroup |
|---:|:---|
| 1 | `1` |
| 2 | `2` |
| 3 | `3+` |
| 4 | `3+` |

Evidence:

- `notebooks/03_machine_learning.ipynb`, cell 9;
- `notebooks/02_statistical_modeling.ipynb`, cell 21.

Values outside this mapping are not assigned to an invented group.

## 7. Model Roles

### Gradient Boosting

Role: primary model.

It has greater operational relevance because it demonstrated the approved
overall predictive balance and generalization.

### Decision Tree

Role: complementary sensitivity model.

It contributes additional sensitivity and may identify churn-risk cases not
detected by the primary model.

The Decision Tree does not override the Gradient Boosting model.

## 8. Processing Flow

```text
CustomerInput
      ↓
Input validation
      ↓
ProductsGroup derivation
      ↓
Metadata-aligned single-row DataFrame
      ↓
Gradient Boosting prediction
      ↓
Decision Tree prediction
      ↓
Four-level decision policy
      ↓
Agreement/disagreement interpretation
      ↓
Operational recommendation
      ↓
Presentation
```

Each stage must remain independently testable.

## 9. Input-Building Contract

The input-building stage must:

1. validate all customer fields;
2. derive `ProductsGroup`;
3. map domain attributes to exported feature names;
4. construct exactly one row;
5. use metadata-declared feature order;
6. verify feature count;
7. apply or verify semantic dtypes;
8. exclude the target and any extra field.

The input-building stage must not:

- load artifacts;
- execute models;
- apply the decision policy;
- render Streamlit components.

## 10. Independent Model Predictions

Each model must produce an independent `ModelPrediction` containing, as
supported by the domain contract:

- model identity;
- predicted class;
- probability when available.

Predicted classes must remain visible after consolidation.

## 11. Decision Policy

The approved risk policy is defined by the canonical feature specification:

`docs/features/churn-risk-orchestration.md`

### Semantics

#### LOW

Neither model detected sufficient evidence of churn.

#### MODERATE

Only the complementary sensitivity model predicted churn.

This result represents additional evidence detected by the Decision Tree while
the primary model remained negative.

#### HIGH

The primary Gradient Boosting model predicted churn while the Decision Tree
remained negative.

The primary model prediction gives this result greater operational relevance
than `MODERATE`.

#### CRITICAL

Both models predicted churn.

This is the strongest agreement available within the approved policy.

## 12. Forbidden Consolidation Rules

The feature must not replace the approved policy with:

- majority voting;
- a final binary logical OR;
- arithmetic mean of probabilities;
- weighted average of probabilities;
- summed probabilities;
- an invented combined probability.

Any policy change requires explicit human approval and corresponding updates to
requirements, feature specification, metadata, code, tests, and traceability.

## 13. Probability Handling

When `predict_proba` is available:

- retain the Gradient Boosting churn probability;
- retain the Decision Tree churn probability;
- associate each probability with its model identity.

The feature must not produce a consolidated probability.

Probability values must not be described as certainty.

## 14. Interpretation Rules

The interpretation stage must identify whether the models agree.

### Agreement

- both predict non-churn: explain that neither model detected sufficient churn evidence;
- both predict churn: explain that both models detected churn evidence.

### Disagreement

- Gradient Boosting `0`, Decision Tree `1`: explain that only the more sensitive complementary model detected churn evidence;
- Gradient Boosting `1`, Decision Tree `0`: explain that the primary model detected churn evidence while the complementary model did not.

Interpretation must not change the risk policy.

## 15. Recommendation Rules

A recommendation must be selected according to the consolidated risk level.

The recommendation:

- supports analyst action;
- is not a model probability;
- is not an automatic decision;
- must remain non-deterministic;
- must be presented separately from model evidence.

Detailed recommendation wording may be implemented in a dedicated presentation
or interpretation specification.

## 16. Error Scenarios

The feature must stop without producing a complete result when:

- customer input is invalid;
- the derived feature cannot be constructed;
- metadata schema is incompatible;
- a required artifact is missing;
- an artifact hash does not match;
- a pipeline cannot be loaded;
- a model lacks required prediction behavior;
- prediction output is malformed;
- reference behavior is inconsistent.

Partial model output must not be presented as a completed consolidated result.

## 17. Operational Sources

Operational artifact details are defined by:

- `artifacts/metadata.json`;
- `artifacts/reference_predictions.csv`;
- repository-controlled `.joblib` pipelines.

The feature specification defines the meaning of the behavior. Operational
metadata defines the exported artifact contract.

## 18. Acceptance Criteria

The feature is complete when:

- valid customer input becomes exactly one metadata-compatible row;
- `ProductsGroup` matches the training-time transformation;
- both pipelines execute independently;
- both predictions are retained;
- both probabilities remain separate when available;
- exactly one approved risk level is returned;
- agreement or disagreement is explained;
- an operational recommendation is included;
- no deterministic certainty claim is made;
- reference predictions remain valid;
- relevant tests and quality checks pass.

## 19. Deferred Responsibilities

Until explicitly implemented by later tasks, the following may remain deferred:

- final Streamlit composition;
- visual styling;
- recommendation wording;
- application-level caching;
- deployment configuration;
- telemetry and analytics;
- external integrations.
