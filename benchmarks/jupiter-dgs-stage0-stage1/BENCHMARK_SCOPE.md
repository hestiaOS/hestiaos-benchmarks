# Benchmark Scope

## Purpose

External, reproducible validation of HestiaOS as a **governance substrate** and research-acceleration platform,
runnable in an unknown external research environment (e.g. a JUPITER/JSC playground allocation).

## Working assumption

Hardware, scheduler, container rules, and data policy are **unknown** until probed. No accelerator access is
assumed. Minimal allocation first.

## Core question

> Does a deterministic governance substrate, operationalised through DSGK + CEG + CausalTraceGraph, produce
> measurable advantages over ungated agent execution, when both run identical tasks under equivalent inference
> budget in an external research environment?

## Non-goals

- No foundation-model training.
- No production / Jülich / JUPITER validation claim.
- No scale-out as a core claim.
- No Moirai/RPIL as a Stage-1 runtime requirement. `moirai/` is a clean Moirai source basis only after `MOIRAI-BASELINE-01`; the benchmark harness remains separate and stage-gated.
- No externally effective or destructive actions.

## Source basis boundary

`moirai/` is available as a clean Moirai source candidate after baseline review (`moirai/docs/MOIRAI_BASELINE_01.md`). Stage 0/1 may use it as contextual source input for CR-01 planning, but Stage 0/1 do not depend on Moirai at runtime and do not claim a completed Moirai emergence benchmark.

## Stage 0 — Portability & Environment Baseline

Read-only probe of the environment (python, platform, disk, allowlisted env vars, container/scheduler hints,
git availability, import checks, write test). Outputs an environment profile + portability gap report. No
network, no GPU benchmark, no scheduler jobs.

## Stage 1 — Core DGS Benchmark (A/B)

Deterministic, model-free (`--mode mock`) A/B over a fixed task set (T01–T08):
- **baseline**: ungated simulated agent output; effect always applied (sandbox only).
- **governed**: explicit intent → governance decision → controlled effect/block → causal trace → replay fields.

Metrics are defined **before** the run (see `benchmark/metrics.py`): task_success, unsafe_action_prevention,
duplicate_intent_handling, stale_intent_handling, conflict_handling, audit_completeness, replay_success,
runtime_overhead_proxy, artifact_completeness. `audit_completeness` is a countable field list.

## Stage 2 — Outlook only (NOT executed in this sprint)

Optional later: `--mode local-model` against a local Ollama model (if `OLLAMA_MODEL` is set and policy allows),
richer tasks, multiple seeds, statistical aggregation. Documented as a direction, not built here.

## Stage 3 — Out of sprint (explicitly excluded)

Scale-out, multi-node, scheduler-driven large runs, accelerator benchmarks — explicitly **out of scope**.

## Safety frame

Sandbox-only effects; no network; no external/destructive actions; no secrets recorded; read-only environment
probe; no real HPC/scheduler jobs started.

## Evidence boundary

Reports are written only into the local `reports/<run_id>/` tree. Submitted snapshots are separated from
post-submission progress (see CLAIM_BOUNDARY.md).

## Success criterion

Stage 0 and Stage 1 (mock) run locally with **no external dependencies**, produce reproducible reports, with
pre-defined metrics and separately stored A/B variants.
