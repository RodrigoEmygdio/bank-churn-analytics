---
name: engineering-governance
description: >
  Coordinates engineering governance activities across architecture,
  implementation, requirements, documentation, traceability, and
  knowledge preservation. Ensures every engineering fact has a single
  canonical authority and that repository artifacts remain semantically
  consistent as the system evolves.
---

# Engineering Governance

## Purpose

Use this skill whenever a change may affect more than source code.

Engineering governance preserves the integrity of engineering knowledge by ensuring:

- semantic consistency;
- canonical ownership;
- documentation synchronization;
- architectural traceability;
- implementation status accuracy;
- knowledge preservation.

This skill coordinates specialized governance skills instead of replacing them.

---

# Core Principle

Engineering knowledge has ownership.

Every engineering fact must have exactly one canonical authority.

All other occurrences are:

- derived references;
- explanatory summaries;
- historical records;
- implementation evidence.

No engineering knowledge should silently acquire multiple authoritative sources.

---

# Governance Responsibilities

Engineering governance is responsible for:

- classifying engineering changes;
- identifying impacted artifacts;
- resolving documentation authority;
- preserving architectural intent;
- synchronizing implementation status;
- maintaining traceability;
- preventing semantic drift;
- coordinating governance workflows.

It is **not** responsible for implementing features.

---

# Engineering Artifact Taxonomy

Before updating any artifact, classify the engineering information.

| Engineering Information | Canonical Artifact |
|-------------------------|-------------------|
| Business rules | Feature Specification |
| Decision tables | Feature Specification |
| User-visible behavior | Functional Requirements |
| Quality attributes | Non-Functional Requirements |
| Architectural rationale | ADR |
| Runtime metadata | metadata.json |
| Domain contracts | Domain |
| Implementation progress | Implementation Traceability |
| Validation behavior | Tests |
| Operational procedures | Runbooks / Operational Docs |

Never update documentation before identifying the canonical owner.

---

# Documentation Authority Resolution

Whenever identical or similar engineering information appears in multiple documents:

1. Identify the engineering fact.

2. Locate the canonical owner.

3. Determine whether every other occurrence is:

   - canonical;
   - derived;
   - explanatory;
   - historical.

4. Update the canonical source first.

5. Synchronize derived documents.

6. Remove duplicated normative definitions whenever possible.

7. Verify no conflicting authority remains.

Never silently create multiple canonical sources.

---

# Governance Workflow

Every engineering change must follow this workflow.

Engineering Change

↓

Semantic Classification

↓

Canonical Ownership Resolution

↓

Impact Analysis

↓

Specialized Governance Skills

↓

Consistency Validation

↓

Completion Report

---

## Semantic Classification

First determine the nature of the change.

Possible categories include:

- behavioral;
- architectural;
- operational;
- implementation;
- documentation;
- contractual;
- metadata;
- testing.

A change may belong to multiple categories.

---

## Impact Analysis

Identify every engineering artifact potentially affected.

Typical artifacts include:

- domain contracts;
- implementation;
- feature specifications;
- requirements;
- ADRs;
- implementation traceability;
- metadata;
- tests;
- operational documentation.

Do not assume only code changes.

---

## Skill Coordination

Invoke specialized governance skills whenever applicable.

Typical routing:

Implementation changes
→ Documentation Governance

Architectural decisions
→ ADR Quality Rubric

Documentation updates
→ Documentation Governance

Requirement modifications
→ Documentation Governance

Traceability changes
→ Documentation Governance

Multiple skills may be required.

---

# Governance Validation

Before completion verify:

- exactly one canonical owner exists for every engineering fact;
- no duplicated normative definitions remain;
- terminology is globally consistent;
- implementation status reflects repository reality;
- deferred responsibilities remain correctly identified;
- cross-document references remain valid;
- architectural intent has been preserved.

---

# Engineering Knowledge Graph

Reason about repository knowledge as connected engineering concepts.

Example:

RiskLevel

├── Domain Contract

├── Feature Specification

├── Functional Requirement

├── Tests

├── Traceability

└── ADR

When one node changes:

- identify connected artifacts;
- evaluate semantic impact;
- synchronize only affected artifacts.

Do not perform repository-wide replacement.

---

# Prohibited Behavior

Never:

- perform blind search-and-replace across documentation;
- infer requirements solely from implementation;
- treat implementation as automatic specification authority;
- create duplicated decision tables;
- promote explanatory text into canonical specification;
- update unrelated artifacts;
- mark implementation complete without evidence;
- change implementation status because files merely exist.

---

# Completion Report

Return:

## Engineering Change

Describe what changed.

## Semantic Classification

List every identified category.

## Canonical Authority

Identify the authoritative artifact.

## Impact Analysis

List every affected engineering artifact.

## Skills Invoked

List governance skills executed.

## Repository Updates

Summarize changes.

## Consistency Validation

Describe performed validation.

## Remaining Risks

List unresolved governance questions.

## Final Status

READY

or

HUMAN REVIEW REQUIRED