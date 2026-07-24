# AGENTS.md

## 1. Purpose

This file defines how coding agents must work in this repository.

Product behavior, quality attributes, feature behavior, architectural decisions,
and operational artifact contracts are defined in specialized sources:

- `docs/requirements/functional/`
- `docs/requirements/non-functional/`
- `docs/features/`
- `docs/architecture/`
- `artifacts/metadata.json`
- `artifacts/reference_predictions.csv`

Do not treat this file as the runtime specification of the application.

## 2. Project Context

This repository contains a decision-support application for bank-customer churn
analysis using trained Machine Learning pipelines.

The project is both:

- an academic Machine Learning delivery;
- a software-engineering portfolio demonstrating investigation, ML engineering,
  architecture, artifact governance, testing, and AI-assisted development.

Agents must preserve this dual purpose by favoring traceability, reproducibility,
clear boundaries, and professional implementation quality.

## 3. Authority and Required Reading

Before editing code, inspect only the sources relevant to the task.

Use this precedence:

1. explicit human-approved instructions;
2. applicable accepted ADRs;
3. applicable feature specifications;
4. applicable functional and non-functional requirements;
5. implementation traceability;
6. operational metadata and repository-controlled artifacts;
7. existing code and tests;
8. this file as an agent-working guideline.

Use each source only for its intended responsibility.

If authoritative sources disagree:

- stop;
- identify the conflicting sources;
- describe the impact;
- request human review.

Do not silently invent or reconcile product behavior.

## 4. Change Discipline

### Before editing

- inspect the affected modules and tests;
- identify applicable requirements, feature specifications, and ADRs;
- inspect operational metadata when the task touches model artifacts or schema;
- propose or apply the smallest coherent change;
- identify deferred responsibilities explicitly.

### During editing

- keep the patch focused;
- avoid unrelated refactoring;
- preserve approved architectural boundaries;
- add or update tests for behavior changes;
- update traceability when architecture or responsibilities change;
- do not overwrite serialized model artifacts.

### After editing

- run applicable tests;
- run linting and formatting checks;
- inspect the final diff;
- confirm no model artifact was modified;
- report anything that remains unverified.

## 5. Engineering Guidelines

Use:

- English code and identifiers;
- explicit type hints;
- descriptive names;
- small, deterministic functions;
- immutable contracts where practical;
- `pathlib.Path`;
- explicit exception types;
- exception chaining when preserving lower-level context;
- pure functions for deterministic business logic;
- minimal dependencies.

Avoid:

- broad exception handling that hides failures;
- global mutable state;
- duplicated contracts;
- undocumented constants;
- hidden file I/O at import time;
- premature frameworks or abstractions;
- dynamic imports without architectural need;
- silent coercion of invalid data;
- mixing UI, artifact loading, inference, and business policy.

The user-facing interface may be written in Portuguese.

## 6. Architectural Discipline

Maintain the dependency direction defined by accepted ADRs and implementation
traceability.

At minimum, preserve separation between:

- domain contracts;
- artifact loading and integrity;
- input validation and feature construction;
- model inference;
- decision policy;
- interpretation;
- presentation;
- application composition.

Do not move implementation-specific product rules into this file.

Concrete behavior belongs in:

- functional requirements;
- non-functional requirements;
- feature specifications;
- ADRs;
- operational metadata;
- code and tests.

## 7. Repository and Artifact Safety

- Load only repository-controlled artifacts.
- Never load user-provided or remote serialized model files.
- Never accept arbitrary artifact paths from the UI.
- Never retrain models inside the application unless explicitly requested.
- Never modify serialized artifacts at runtime.
- Do not suppress compatibility warnings without justification.
- Do not persist customer input.
- Do not add telemetry, analytics, network calls, or external services without
  explicit approval.

## 8. Dependency Management and Commands

Use `uv` and the commands configured by the repository.

Relevant commands may include:

```bash
uv sync
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run streamlit run app.py
```

Run all checks relevant to the task.

If a command cannot be executed, report:

- the command;
- why it failed or was unavailable;
- what remains unverified.

Do not claim that a check passed unless it was executed successfully.

## 9. Testing Discipline

Every implementation task must preserve or add tests when behavior changes.

Prefer tests that validate:

- public contracts;
- architectural boundaries;
- deterministic business rules;
- repository-controlled artifact compatibility;
- reference behavior;
- error semantics.

Tests must not retrain the models.

Do not update expected reference outputs automatically when tests fail.

## 10. Documentation Discipline

Update documentation when:

- product behavior changes;
- a quality attribute changes;
- an ADR is accepted or superseded;
- module responsibilities change;
- a feature contract changes;
- operational assumptions change.

Do not duplicate full product specifications in this file.

## 11. Definition of Done

A task is complete only when:

- requested behavior is implemented;
- applicable requirements are satisfied;
- architectural boundaries remain respected;
- tests cover the changed behavior;
- relevant checks pass;
- no model artifact was modified;
- documentation is updated when necessary;
- unresolved risks are reported honestly.

## 12. Agent Response Format

At the end of each coding task, report exactly these sections:

## Implemented

Brief summary of the completed work.

## Files Changed

List the relevant created or modified files.

## Validation

List commands executed and their results.

## Remaining Risks

List only unresolved, deferred, or unverified items.

Do not provide generic success claims.
Do not hide failed or skipped validation.
