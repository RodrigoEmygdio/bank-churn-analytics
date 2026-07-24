---
name: adr-quality-rubric
description: Evaluates Architecture Decision Records with a repeatable quality rubric covering decision clarity, rationale, evidence traceability, alternatives, boundaries, consequences, and consistency before human approval.
---

# ADR Quality Rubric

## Purpose

Use this skill to review an Architecture Decision Record before human approval or to remediate weak ADR sections.

The rubric checks whether an ADR records a durable, evidence-based architectural decision instead of an implementation proposal.

## Workflow

1. Read the ADR and identify its status, scope, decision, and evidence sources.
2. Load `references/rubric.md` for the full scoring criteria.
3. Score each criterion from `0` to `5`.
4. Check critical defects that block approval regardless of score.
5. Report findings with specific ADR sections and actionable remediation.
6. Do not treat the numeric score as the only approval criterion.

## Critical Criteria

An ADR is not ready when any of these criteria score below `3`:

- Decision Quality;
- Architectural Reasoning;
- Evidence Traceability;
- Alternatives Analysis;
- Internal Consistency.

## Output Expectations

Report:

- total score and classification;
- per-criterion findings;
- critical defects, if any;
- required remediation before approval;
- residual risks or open questions.

## References

- `references/rubric.md`: complete rubric, score guide, quality gates, review questions, and critical defect checks.
