# Playground Runbook

> Assume nothing about the target environment.

```
Hardware unknown
Scheduler unknown
Container rules unknown
Data policy unknown
No assumption of accelerator access
Minimal allocation first
```

## Procedure

```
1. Clone / copy this package into the allocation (no install needed; stdlib only).
2. Run Stage 0:
     python3 benchmark/run_stage0_environment_probe.py --out reports
3. Review reports/<run_id>/PORTABILITY_GAP_REPORT.md
     -> confirm reports dir writable; note any gaps/assumptions.
4. If GO: run Stage 1 mock benchmark:
     python3 benchmark/run_stage1_dgs_benchmark.py --mode mock --out reports
5. Collect reports/<run_id>/ (DGS_BENCHMARK_REPORT.md + aggregate_metrics.json + baseline/ + governed/).
6. Redact traces if needed (hashes are already short, non-secret; review before sharing externally).
7. Decide whether local-model / scheduler execution is allowed (Stage 2 outlook) — only after policy review.
8. OPTIONAL Stage 2 (only after a Stage-1 go): explore optional_stage2_science_trace/ (richer provenance
   library, stdlib-only, no ISO/build). See optional_stage2_science_trace/STAGE2_RUNBOOK.md.
```

Stage 0/1 remain the primary path. Stage 2 is optional and never a prerequisite.

## Hard rules in the playground

```
- No network calls. No external/destructive actions.
- No real HPC/scheduler jobs started by this kit.
- No secrets recorded (env capture is allowlist-only).
- Effects are sandbox-only and simulated in mock mode.
- Stage 2 (local-model) only after explicit policy clearance; Stage 3 (scale-out) out of scope.
```

## What to share as evidence

```
reports/<run_id>/PLAYGROUND_ENVIRONMENT_PROFILE.md
reports/<run_id>/PORTABILITY_GAP_REPORT.md
reports/<run_id>/DGS_BENCHMARK_REPORT.md
reports/<run_id>/aggregate_metrics.json
(+ baseline/ and governed/ per-task folders if full evidence is requested)
```
