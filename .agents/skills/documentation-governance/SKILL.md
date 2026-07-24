---
name: documentation-governance
description: >
  Classifies and synchronizes engineering documentation according to
  document purpose, architectural authority, and canonical ownership.
---

# Documentation Governance

## Purpose

Use this skill whenever a code, architecture, requirement, artifact,
or domain-contract change may require documentation updates.

## Mandatory Workflow

1. Identify the semantic change.
2. Classify the changed information.
3. Locate the canonical document.
4. Inspect derived references.
5. Update the canonical source first.
6. Update references without creating duplicated authority.
7. Remove stale or misplaced content.
8. Validate terminology and implementation state.
9. Report every documentation decision.

## Document Classification

### Feature Specification
Business behavior, flows, decision tables, semantics, inputs and outputs.

### Functional Requirement
Externally observable system obligations.

### Non-Functional Requirement
Quality attributes and operational constraints.

### ADR
Architectural decisions, alternatives, rationale and consequences.

### Implementation Traceability
Mapping between specification, implementation, status and deferred work.

### Operational Metadata
Runtime artifact facts and machine-readable operational contracts.

## Canonical Ownership Rules

- Business decision tables belong to feature specifications.
- Quality constraints belong to non-functional requirements.
- Architectural rationale belongs to ADRs.
- Implementation status belongs to traceability.
- Runtime model facts belong to operational metadata.
- Tests verify behavior but are not specification authority.
- Existing code is evidence, not automatically the source of truth.

## Duplication Policy

Do not duplicate normative content unless explicitly required.

When another document needs the information:

- reference the canonical document;
- summarize only what is necessary for local context;
- clearly state which document is authoritative.

## Semantic Review Questions

Before editing documentation, answer:

1. What changed?
2. Is the change behavioral, architectural, operational, or qualitative?
3. Which document owns this information?
4. Does another document currently duplicate it?
5. Should that duplicate be removed, summarized, or converted into a reference?
6. Does the implementation traceability status need to change?
7. Are deferred responsibilities still accurate?
8. Did terminology change across contracts, requirements, tests, and metadata?

## Prohibited Behavior

- Do not perform blind global replacement across documentation.
- Do not move business semantics into non-functional requirements.
- Do not treat implementation traceability as a feature specification.
- Do not mark a component implemented solely because a related file exists.
- Do not derive requirements only from current code.
- Do not introduce a second canonical decision table.
- Do not update documentation unrelated to the semantic change.

## Required Validation

Search for:

- obsolete terminology;
- duplicate normative tables;
- conflicting status labels;
- stale deferred responsibilities;
- references to removed contracts;
- inconsistent enum or field names.

## Completion Report

### Semantic Change
Describe what changed.

### Classification
State the document category and why.

### Canonical Source
Identify the authoritative document.

### Documents Updated
Explain each modification.

### Duplication Removed
List redundant or misplaced content removed.

### Consistency Checks
Report searches and validations performed.

### Unresolved Ambiguities
List decisions requiring human authority.