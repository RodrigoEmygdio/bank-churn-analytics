---
name: adr-writing
description: Guides creation, review, and revision of Architecture Decision Records that preserve architectural decisions, rationale, alternatives, consequences, and evidence without drifting into implementation detail.
---

# ADR Writing

## Purpose

Use this skill when creating, reviewing, revising, or extending Architecture Decision Records.

The goal is to produce ADRs that document durable architectural decisions and remain valid as implementation details evolve.

## Workflow

1. Confirm the decision scope and ADR status.
2. Gather approved evidence, constraints, existing ADRs, and human decisions.
3. Separate architecture from implementation mechanics.
4. Compare meaningful alternatives with advantages, disadvantages, and suitability.
5. Record the decision, rationale, consequences, constraints, validation criteria, and open questions.
6. Self-review for evidence traceability, internal consistency, and durability.

## Core Rules

- Do not invent architectural decisions.
- Explain why the decision exists, not merely how code is organized.
- Prefer logical responsibilities and dependency boundaries over filenames and classes.
- Treat implementation details as architectural only when explicitly approved as such.
- Rejected alternatives must be rejected for architectural reasons, not because another instruction file says so.

## References

Read only the references needed for the task:

- `references/workflow.md`: ADR authoring flow.
- `references/principles.md`: durable ADR writing principles.
- `references/template.md`: baseline ADR structure.
- `references/checklist.md`: review checklist.
- `references/review.md`: self-review prompts.
- `references/anti-patterns.md`: examples of weak ADR content.
- `references/original-skill.md`: original skill text preserved for traceability.
