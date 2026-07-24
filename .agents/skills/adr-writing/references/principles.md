# ADR Writing Principles

## Principle 1

Architecture documents decisions.

Implementation documents code.

---

## Principle 2

Every decision must answer:

- What?
- Why?
- Why not the alternatives?

---

## Principle 3

Every accepted decision should be traceable to technical evidence.

Examples:

- benchmark;
- notebook;
- ML evaluation;
- performance analysis;
- architectural discussion.

---

## Principle 4

Describe logical responsibilities before physical implementation.

Prefer:

Presentation Layer

Avoid:

ui/result.py

unless the physical structure was explicitly approved.

---

## Principle 5

An ADR must survive implementation refactoring.

Changing folders should not invalidate the ADR.

---

## Principle 6

Avoid implementation prescriptions.

Do not define:

- filenames;
- packages;
- frameworks;
- class names;

unless they are themselves architectural decisions.

---

## Principle 7

Rejected alternatives must explain why they were rejected.

Never write:

"Rejected because AGENTS.md forbids it."

Instead explain the architectural reasoning.

---

## Principle 8

Architecture preserves knowledge.

Implementation realizes knowledge.

The ADR exists to preserve the architectural knowledge produced during earlier project phases.

---

## Principle 9

Do not mix:

- architecture;
- implementation;
- testing;
- CI;
- coding standards.

Each belongs to its own document.

---

## Principle 10

Prefer responsibilities over files.

Good:

Prediction Layer

Bad:

prediction_service.py