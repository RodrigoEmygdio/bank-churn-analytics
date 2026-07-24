# ADR Writing Skill

## Purpose

This skill guides an AI agent to produce Architecture Decision Records (ADRs) that document architectural decisions rather than implementation details.

The objective is to produce ADRs that remain valid even if the implementation evolves.

---

## When to use

Use this skill whenever:

- creating a new ADR;
- revising an ADR;
- reviewing an ADR;
- extending an existing ADR.

---

## Inputs

The agent should use:

- approved repository diagnosis;
- approved architectural discussions;
- existing ADRs;
- project constraints;
- technical evidence (ML reports, notebooks, benchmarks, experiments).

Never invent architectural decisions.

---

## Expected Output

A complete ADR that:

- documents decisions;
- explains rationale;
- compares alternatives;
- records consequences;
- remains implementation independent.

---

## Core Principle

An ADR documents **why** an architectural decision exists.

It does not document **how** the implementation is written.