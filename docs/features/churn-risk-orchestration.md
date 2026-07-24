# Feature Specification — Churn Risk Orchestration

## Decision Policy

This document is the canonical feature specification for the four-level churn
risk decision table.

The Decision Policy consumes a completed `PredictionResult` and returns only a
`RiskLevel`. It uses predicted classes only. Model-specific probabilities are
preserved as evidence for later presentation but do not alter the policy.

| Gradient Boosting | Decision Tree | Risk Level |
|---:|---:|:---|
| 0 | 0 | `LOW` |
| 0 | 1 | `MODERATE` |
| 1 | 0 | `HIGH` |
| 1 | 1 | `CRITICAL` |

## Semantics

`LOW`: neither model indicates churn risk.

`MODERATE`: only the sensitivity-oriented Decision Tree indicates churn risk.

`HIGH`: the primary Gradient Boosting model indicates churn risk.

`CRITICAL`: both independent model signals indicate churn risk.

## Constraints

The policy must not average, sum, compare, threshold, calibrate, or otherwise
combine probabilities.

The policy must not execute models, load artifacts, construct features,
interpret results, generate recommendations, or render presentation output.
