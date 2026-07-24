# ADR Quality Rubric

## Purpose

This rubric provides a repeatable method for evaluating the quality of an Architecture Decision Record before it is submitted for human approval.

It is intended to support:

- ADR authoring;
- automated self-review;
- architectural review;
- remediation of weak ADR sections;
- consistent quality across projects.

The rubric evaluates whether an ADR records a durable, evidence-based architectural decision rather than merely documenting an implementation proposal.

---

## Evaluation Method

Each criterion receives a score from `0` to `5`.

| Score | Meaning |
|---:|---|
| 0 | Missing or fundamentally incorrect |
| 1 | Very weak; major revision required |
| 2 | Partially addressed; significant gaps remain |
| 3 | Acceptable baseline; improvements recommended |
| 4 | Strong; only minor improvements required |
| 5 | Excellent; clear, complete, and architecturally mature |

The maximum score is `40`.

The final score must not be used as the only approval criterion. Critical architectural defects may block approval regardless of the total score.

---

## Quality Gates

| Score | Classification | Expected Action |
|---:|---|---|
| 36–40 | Excellent | Ready for human approval |
| 31–35 | Strong | Minor review recommended |
| 24–30 | Acceptable with reservations | Revision required before approval |
| 16–23 | Weak | Significant remediation required |
| 0–15 | Unacceptable | Rewrite the ADR |

An ADR must not be considered ready for approval when any critical criterion receives a score below `3`.

Critical criteria:

- Decision Quality;
- Architectural Reasoning;
- Evidence Traceability;
- Alternatives Analysis;
- Internal Consistency.

---

# Evaluation Criteria

## 1. Decision Quality

### Evaluation Question

Does the ADR clearly state the architectural decision being proposed or accepted?

### Score Guide

#### 0 — Missing

- No identifiable decision exists.
- The document only describes context, implementation, or requirements.

#### 1 — Very Weak

- The decision is vague or ambiguous.
- Multiple unrelated decisions are mixed together.
- The reader cannot determine what is actually being approved.

#### 2 — Partial

- A decision is present but poorly bounded.
- Important parts remain implicit.
- The decision is mixed with implementation details.

#### 3 — Acceptable

- The main architectural decision is identifiable.
- Scope and intent are mostly clear.
- Some refinement may still be necessary.

#### 4 — Strong

- The decision is explicit, scoped, and understandable.
- Architectural intent is distinguished from implementation.

#### 5 — Excellent

- The decision is precise, bounded, durable, and unambiguous.
- The reader understands exactly what is being decided and what is outside the decision scope.

### Review Questions

- What exactly is being approved?
- Is the decision architectural?
- Is the scope clearly bounded?
- Are unrelated decisions separated?

---

## 2. Architectural Reasoning

### Evaluation Question

Does the ADR explain why the decision is architecturally appropriate?

### Score Guide

#### 0 — Missing

- No rationale is provided.

#### 1 — Very Weak

- The rationale is circular.
- Example: “This option was rejected because another document forbids it.”

#### 2 — Partial

- Some reasoning exists, but it relies mainly on preference or convention.
- Architectural trade-offs are poorly explained.

#### 3 — Acceptable

- The main reasoning is present.
- Relevant trade-offs are acknowledged.

#### 4 — Strong

- The rationale connects the decision to architectural drivers and project needs.
- Trade-offs are explained clearly.

#### 5 — Excellent

- The decision follows logically from the context, evidence, constraints, and decision drivers.
- The reasoning explains both the benefits and the accepted costs.

### Review Questions

- Why was this decision made?
- Which project problem does it solve?
- Which trade-offs were consciously accepted?
- Does the reasoning go beyond “best practice”?

---

## 3. Evidence Traceability

### Evaluation Question

Can the decision be traced to approved technical or business evidence?

### Relevant Evidence

Evidence may include:

- repository diagnosis;
- Machine Learning notebooks;
- model evaluation reports;
- benchmarks;
- experiments;
- production incidents;
- architectural discussions;
- user-approved corrections;
- requirements;
- existing system constraints.

### Score Guide

#### 0 — Missing

- No evidence is referenced or reflected.

#### 1 — Very Weak

- Claims are unsupported.
- The ADR appears to invent assumptions.

#### 2 — Partial

- Some evidence is mentioned, but the relationship to the decision is weak.

#### 3 — Acceptable

- Important decisions are connected to identifiable evidence.

#### 4 — Strong

- Most decisions and rejected alternatives are traceable to approved evidence.

#### 5 — Excellent

- Architectural decisions, constraints, and alternative rejections are explicitly derived from prior evidence.
- Facts, inferences, recommendations, and human-approved decisions remain distinguishable.

### Review Questions

- Which evidence supports this decision?
- Did the ADR preserve conclusions from previous project stages?
- Are claims traceable to repository-controlled or human-approved sources?
- Did the agent invent any architectural premise?

---

## 4. Alternatives Analysis

### Evaluation Question

Does the ADR fairly compare meaningful alternatives?

### Score Guide

#### 0 — Missing

- No alternatives are considered.

#### 1 — Very Weak

- Alternatives are listed only to justify a predetermined decision.
- Rejections are superficial.

#### 2 — Partial

- Some alternatives are considered, but advantages, disadvantages, or suitability are incomplete.

#### 3 — Acceptable

- Relevant alternatives are described with reasonable trade-offs.

#### 4 — Strong

- Alternatives are compared fairly and rejected for architectural reasons.

#### 5 — Excellent

- The option set is representative and non-trivial.
- Advantages, disadvantages, consequences, and suitability are explicit.
- Rejection reasoning is grounded in evidence and decision drivers.

### Review Questions

- Were realistic alternatives considered?
- Were alternatives represented fairly?
- Are rejection reasons architectural rather than procedural?
- Was the selected option compared against the strongest competing options?

---

## 5. Separation of Architecture and Implementation

### Evaluation Question

Does the ADR focus on durable architectural decisions instead of implementation mechanics?

### Score Guide

#### 0 — Fundamentally Incorrect

- The document is primarily an implementation guide.

#### 1 — Very Weak

- Decisions are expressed mainly as files, classes, packages, or commands.

#### 2 — Partial

- Architectural responsibilities are present, but implementation details dominate.

#### 3 — Acceptable

- Architecture and implementation are mostly separated.
- Some physical details remain but do not obscure the decision.

#### 4 — Strong

- The ADR emphasizes logical responsibilities, boundaries, and constraints.
- Physical details appear only when architecturally relevant or explicitly approved.

#### 5 — Excellent

- The ADR remains valid across ordinary package, module, class, and file refactoring.
- Implementation-specific material is intentionally delegated to separate specifications.

### Review Questions

- Would renaming folders invalidate the ADR?
- Does the ADR describe responsibilities or filenames?
- Are testing tools and CI commands incorrectly embedded?
- Are implementation details themselves architectural decisions?

---

## 6. Architectural Boundaries and Responsibilities

### Evaluation Question

Are component responsibilities and dependency boundaries clear?

### Score Guide

#### 0 — Missing

- No architectural boundaries are described.

#### 1 — Very Weak

- Responsibilities overlap or contradict one another.

#### 2 — Partial

- Some components are defined, but boundaries remain ambiguous.

#### 3 — Acceptable

- Major responsibilities and dependencies are understandable.

#### 4 — Strong

- Components have clear responsibilities.
- Dependency direction and prohibited couplings are defined.

#### 5 — Excellent

- Logical boundaries are precise, cohesive, and independently understandable.
- The architecture clearly distinguishes domain, presentation, validation, infrastructure, inference, and orchestration concerns where applicable.

### Review Questions

- Does every component have one clear architectural responsibility?
- Are dependency directions explicit?
- Are forbidden dependencies identified?
- Is business policy isolated from infrastructure and presentation?

---

## 7. Consequence Quality

### Evaluation Question

Does the ADR document the consequences of accepting the decision?

### Score Guide

#### 0 — Missing

- No consequences are documented.

#### 1 — Very Weak

- Only benefits are listed.
- Costs and risks are ignored.

#### 2 — Partial

- Positive and negative consequences exist, but remain generic.

#### 3 — Acceptable

- Relevant benefits, costs, and operational effects are described.

#### 4 — Strong

- Architectural, operational, testing, and maintenance consequences are clearly differentiated.

#### 5 — Excellent

- The ADR records benefits, costs, risks, limitations, follow-up work, and accepted trade-offs.
- Consequences are directly connected to the selected decision.

### Review Questions

- What becomes easier?
- What becomes harder?
- Which risks remain?
- What operational or maintenance burden is introduced?
- Which future decisions become necessary?

---

## 8. Longevity and Internal Consistency

### Evaluation Question

Will the ADR remain useful over time, and is it internally consistent?

### Score Guide

#### 0 — Fundamentally Incorrect

- The ADR contradicts itself or existing approved decisions.

#### 1 — Very Weak

- Status, decision language, scope, or terminology are inconsistent.
- Example: status is `Proposed`, but the text repeatedly says `approved`.

#### 2 — Partial

- Minor contradictions or unstable implementation coupling exist.

#### 3 — Acceptable

- The ADR is mostly consistent and should survive moderate implementation evolution.

#### 4 — Strong

- Terminology, status, constraints, and decisions are consistent.
- Supersession behavior is defined.

#### 5 — Excellent

- The ADR is internally coherent, durable, and clearly positioned relative to prior and future ADRs.
- Refactoring does not invalidate its core decision.
- Conflicts require explicit amendment or supersession.

### Review Questions

- Does the status match the language used?
- Does the Decision section contradict the alternatives or constraints?
- Does the ADR conflict with previous ADRs?
- Would the document remain meaningful after implementation changes?
- Is supersession behavior explicit?

---

# Critical Defect Checks

The following defects block approval even when the total score is high.

## Invented Decision

The ADR introduces an architectural decision that was neither:

- derived from evidence;
- present in project constraints;
- nor explicitly approved by a human.

### Required Action

Return the decision to the open-questions or recommendations section.

---

## Circular Justification

The ADR justifies a decision only because another instruction file requires it.

Example:

```text
Rejected because AGENTS.md forbids it.
```

### Required Action

Identify and document the underlying architectural or analytical reason.

---

## Implementation Masquerading as Architecture

The ADR defines packages, classes, filenames, commands, or test layouts as though they were architectural decisions without justification.

### Required Action

Rewrite the section using logical responsibilities and boundaries or move the material to an implementation specification.

---

## Missing Evidence for Model Behavior

An ADR involving Machine Learning architecture assigns model roles, combines predictions, defines risk semantics, or rejects model strategies without referring to evaluation evidence.

### Required Action

Trace the decision to model evaluation artifacts, reports, notebooks, or approved analytical conclusions.

---

## Synthetic Machine Learning Claim

The ADR describes an application-level interpretation policy as though it were:

- a new model;
- a formal ensemble;
- a calibrated probability;
- a scientifically validated confidence measure.

### Required Action

Clarify the distinction between model inference and application-level decision orchestration.

---

## Hidden Conflict

The ADR silently contradicts:

- an existing accepted ADR;
- approved repository constraints;
- exported ML artifacts;
- metadata contracts;
- validated analytical conclusions.

### Required Action

Identify the conflict and require amendment, supersession, or explicit human approval.

---

# Scoring Worksheet

```text
ADR: ______________________________________
Reviewer: _________________________________
Date: ____________________________________

1. Decision Quality                         ____ / 5
2. Architectural Reasoning                 ____ / 5
3. Evidence Traceability                   ____ / 5
4. Alternatives Analysis                   ____ / 5
5. Architecture/Implementation Separation  ____ / 5
6. Boundaries and Responsibilities         ____ / 5
7. Consequence Quality                     ____ / 5
8. Longevity and Internal Consistency      ____ / 5

Total                                      ____ / 40
Classification: _________________________________
```

---

# Required Review Output

The reviewing agent must produce the following structure:

```markdown
## ADR Quality Review

### Score

`XX/40 — Classification`

### Criterion Scores

| Criterion | Score | Summary |
|---|---:|---|
| Decision Quality | X/5 | ... |
| Architectural Reasoning | X/5 | ... |
| Evidence Traceability | X/5 | ... |
| Alternatives Analysis | X/5 | ... |
| Architecture/Implementation Separation | X/5 | ... |
| Boundaries and Responsibilities | X/5 | ... |
| Consequence Quality | X/5 | ... |
| Longevity and Internal Consistency | X/5 | ... |

### Critical Defects

- None.

or:

- Critical defect: ...
- Required remediation: ...

### Strengths

- ...
- ...

### Required Revisions

- ...
- ...

### Recommendation

One of:

- Ready for human approval.
- Ready after minor corrections.
- Revision required before approval.
- Significant remediation required.
- ADR rewrite required.
```

---

# Self-Review Protocol

Before returning an authored or revised ADR, the agent must:

1. evaluate the ADR using all eight criteria;
2. identify critical defects;
3. rewrite any section associated with a critical defect;
4. repeat the evaluation;
5. return the ADR only when:
   - no critical defect remains;
   - every critical criterion scores at least `3`;
   - the total score is at least `31/40`.

The quality score must not be inflated to satisfy the threshold.

When the ADR cannot meet the threshold because required evidence or human decisions are missing, the agent must stop and report the missing information instead of inventing it.

---

# Machine Learning ADR Addendum

For ADRs involving Machine Learning systems, additionally verify:

- model roles are grounded in evaluation evidence;
- inference behavior remains consistent with training;
- application orchestration is not misrepresented as a new model;
- model disagreement is preserved when analytically relevant;
- probabilities are not combined without a validated statistical method;
- calibration claims require calibration evidence;
- threshold changes require explicit evaluation evidence;
- exported artifacts remain immutable unless retraining is explicitly approved;
- reference predictions or equivalent reproducibility contracts are preserved;
- operational recommendations avoid deterministic claims about uncertain predictions.

An ML-related ADR that fails any of these checks must not be approved without explicit human review.