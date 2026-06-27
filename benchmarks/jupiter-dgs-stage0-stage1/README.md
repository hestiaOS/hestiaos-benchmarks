# jupiter-dgs-stage0-stage1 (benchmark in hestiaos-benchmarks)

> **Repo role:** `hestiaos/hestiaos-benchmarks` — reproducible test/benchmark harnesses.
> **Benchmark name:** `jupiter-dgs-stage0-stage1`. **Purpose:** portable JUPITER/JSC playground preparation.
> Stage 0/1 are the primary path; optional Stage 2 is **not** part of the Stage-1 core claim.
> Benchmark harness — **not** the Science Edition (that is `science-edition`).

---

# JUPITER Science Demo Kit (Stage 0 / Stage 1)

Portable, reproducible demo kit to evaluate HestiaOS as a **deterministic governance substrate** in an
external research environment — **no external dependencies, stdlib only**.

> Bounded, application-driven benchmark. **Not** a foundation-model, **not** a production claim, **not** a
> formal Jülich/JUPITER validation. See [`CLAIM_BOUNDARY.md`](./CLAIM_BOUNDARY.md).

## Contents

```
README.md  QUICKSTART.md  BENCHMARK_SCOPE.md  CLAIM_BOUNDARY.md  PLAYGROUND_RUNBOOK.md
benchmark/
  tasks.json                          T01–T08 task set
  run_stage0_environment_probe.py     read-only portability & environment probe
  run_stage1_dgs_benchmark.py         deterministic A/B governance benchmark (--mode mock)
  metrics.py                          pre-defined metrics + audit field list
  report_writer.py                    stdlib report helpers
reports/                              run outputs (reports/<run_id>/...)
examples/expected_report_structure.md
```

## Run

```bash
python3 benchmark/run_stage0_environment_probe.py --out reports
python3 benchmark/run_stage1_dgs_benchmark.py --mode mock --out reports
```

## What it measures (A/B)

`baseline` (ungated agent) vs `governed` (intent → decision → trace → controlled effect → replay), over a
fixed task set. Metrics are defined before the run: task_success, unsafe_action_prevention,
duplicate/stale/conflict handling, audit_completeness (countable field list), replay_success,
runtime_overhead_proxy, artifact_completeness.

## Stages

- **Stage 0** — Portability & Environment Baseline (read-only).
- **Stage 1** — Core DGS Benchmark (A/B, model-free mock).
- **Stage 2** — **optional** richer treatment layer (`optional_stage2_science_trace/`): a content-only
  extract of the older Science Edition v1.0.0 causal-trace/provenance library. Not part of the Stage-1 core
  claim; explore only **after a Stage-1 go**. Also the `--mode local-model` outlook lives here.
- **Stage 3** — scale-out, explicitly out of scope.

## Relation to HestiaOS repos (context, not pinned by this kit)

```
hestiaos-core              (governance kernel; context only, not a target)
edition-build-pipeline     (component lock / manifest / validation; context only)
hestiaos-community-edition (clean-room composition; context only)
```
This kit is **self-contained** and does not modify or depend on those repos at runtime.

`moirai/` is now tracked as a clean Moirai source basis after `MOIRAI-BASELINE-01` (`moirai/docs/MOIRAI_BASELINE_01.md`). CR-01 may use that source basis only after baseline review. The Stage 0/1 harness remains separate, deterministic, and stage-gated; this does not claim a completed Moirai emergence benchmark, PyTorch/HuggingFace stack, or JUPITER validation.

## Safety

No network, no external/destructive actions, no real HPC/scheduler jobs, no secrets recorded, sandbox-only
simulated effects. See `PLAYGROUND_RUNBOOK.md`.
