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

## Risk Interpretation

The Risk Interpreter consumes a completed `PredictionResult` and the already
assigned `RiskLevel`. It validates consistency between them and returns a
presentation-neutral `InterpretationResult`.

The interpreter explains the decision. It does not recalculate risk, execute
the Decision Policy, inspect probabilities, generate recommendations, or render
presentation output.

Evidence statements contain only model identity and predicted class.
Rationale statements explain why the observed model combination supports the
already assigned risk level.

### LOW

Title:

```text
Low Churn Risk
```

Summary:

```text
No consistent indication of customer churn was detected.
```

Model agreement:

```text
Both models predicted customer retention.
```

Evidence:

```text
Gradient Boosting predicted retention.
Decision Tree predicted retention.
```

Rationale:

- neither model detected churn;
- the models agree;
- the evidence does not indicate elevated churn risk.

### MODERATE

Title:

```text
Moderate Churn Risk
```

Summary:

```text
The complementary model detected a churn signal that was not confirmed by the primary model.
```

Model agreement:

```text
Only the complementary model predicted churn.
```

Evidence:

```text
Gradient Boosting predicted retention.
Decision Tree predicted churn.
```

Rationale:

- the primary model remained negative;
- the complementary model detected churn;
- this disagreement corresponds to moderate churn risk.

### HIGH

Title:

```text
High Churn Risk
```

Summary:

```text
The primary prediction model detected evidence associated with customer churn.
```

Model agreement:

```text
Only the primary model predicted churn.
```

Evidence:

```text
Gradient Boosting predicted churn.
Decision Tree predicted retention.
```

Rationale:

- the primary model detected churn;
- the complementary model did not confirm the prediction;
- this disagreement corresponds to high churn risk.

### CRITICAL

Title:

```text
Critical Churn Risk
```

Summary:

```text
Independent predictive models consistently detected customer churn indicators.
```

Model agreement:

```text
Both models independently predicted churn.
```

Evidence:

```text
Gradient Boosting predicted churn.
Decision Tree predicted churn.
```

Rationale:

- both models detected churn;
- the evidence is mutually reinforcing;
- this agreement corresponds to critical churn risk.

## Recommendation Engine

The Recommendation Engine consumes an `InterpretationResult` and returns a
presentation-neutral `RecommendationResult`.

Only the interpreted `RiskLevel` determines the recommendation. The engine must
not inspect predicted classes, probabilities, model identities, evidence, or
rationale.

| Risk Level | Priority | Objective | Recommendations | Expected Outcome |
|---|---|---|---|---|
| `LOW` | `LOW` | Maintain customer relationship. | Continue periodic monitoring. Maintain current customer engagement. No immediate retention action is required. | Customer relationship remains stable through normal monitoring. |
| `MODERATE` | `MEDIUM` | Investigate potential early churn indicators. | Review recent customer activity. Monitor account behavior. Consider proactive customer contact if additional indicators emerge. | Potential churn indicators are assessed before escalation. |
| `HIGH` | `HIGH` | Reduce customer churn risk through proactive engagement. | Contact the customer. Review customer satisfaction. Evaluate appropriate retention actions. | Customer retention opportunities are identified before churn occurs. |
| `CRITICAL` | `URGENT` | Execute immediate customer retention strategy. | Initiate urgent retention campaign. Escalate to customer success team. Prioritize executive follow-up if applicable. | Immediate intervention maximizes retention opportunity. |

The recommendation contract must not contain presentation formatting, icons,
colors, HTML, Markdown, generated text, or customer-message content.
