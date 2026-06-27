# Claim Boundary

This document defines exactly what the JUPITER Science Demo does and does **not** claim.

## This demo does NOT claim

- It does **not** claim formal Jülich / JUPITER / JSC validation or endorsement.
- It does **not** train, fine-tune, or evaluate a foundation model.
- It does **not** claim production readiness or a production deployment.
- It does **not** claim scale-out / HPC performance as a core result.
- It does **not** perform externally effective or destructive actions.
- It does **not** claim that the Moirai emergence benchmark, PyTorch/HuggingFace stack, or JUPITER pilot is complete.

## This demo DOES evaluate (bounded, application-driven)

- **Reproducibility**: deterministic, model-free runs that reproduce the same report structure on unknown infra.
- **Auditability**: a countable evidence path (intent → decision → trace → effect → replay), measured via
  `audit_completeness` over a fixed field list.
- **Controllability**: governed handling of unsafe / duplicate / stale / conflicting intents vs an ungated baseline.
- **Evidence completeness**: presence of the expected per-variant artifacts.

## Moirai source-basis boundary

`moirai/` is a clean source basis after `MOIRAI-BASELINE-01` and may inform CR-01 follow-up work. It is not a runtime dependency of this Stage-0/1 harness and does not upgrade this harness from deterministic mock evaluation to a completed Moirai emergence benchmark.

## Evidence separation

- The **submitted snapshot** (reports generated for a given submission) must be kept separate from
  **post-submission progress**. Later improvements do not retroactively change submitted evidence.
- Each run is identified by a `run_id`; submitted evidence references specific `run_id`s.

## Working hypothesis (not a proven claim)

> A deterministic governance substrate (DSGK + CEG + CausalTraceGraph-style evidence path) yields measurable
> advantages in auditability, controllability, and replayability over ungated agent execution, under identical
> tasks and equivalent inference budget. This demo provides a bounded, reproducible **test harness** for that
> hypothesis — not a final verdict.
