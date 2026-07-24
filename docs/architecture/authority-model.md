# Authority Model

This project separates architectural authority from operational authority.

## Human Authority

Highest authority.

Any approved human decision overrides previous implementation.

---

## Architectural Authority

Defines how the software should be built.

Examples:

- ADRs
- Architecture documents
- Implementation Traceability

---

## Functional Authority

Defines what the application must do.

Examples:

- Functional Requirements
- Feature Specifications

---

## Non-Functional Authority

Defines required quality attributes.

Examples:

- Reliability
- Security
- Explainability
- Maintainability

---

## Operational Authority

Defines exported ML artifacts.

Examples:

metadata.json

reference_predictions.csv

serialized pipelines

---

## Agent Guidance

AGENTS.md

Defines only how coding agents should work.

It never defines runtime behavior.