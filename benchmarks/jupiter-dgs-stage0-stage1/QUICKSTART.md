# Quickstart

No external dependencies — Python 3 standard library only.

```bash
# Stage 0: read-only environment & portability probe
python3 benchmark/run_stage0_environment_probe.py --out reports

# Stage 1: deterministic, model-free A/B governance benchmark
python3 benchmark/run_stage1_dgs_benchmark.py --mode mock --out reports
```

Outputs land in `reports/<run_id>/`. Key files:

```
reports/<run_id>/PLAYGROUND_ENVIRONMENT_PROFILE.md   (stage 0)
reports/<run_id>/PORTABILITY_GAP_REPORT.md           (stage 0)
reports/<run_id>/DGS_BENCHMARK_REPORT.md             (stage 1)
reports/<run_id>/aggregate_metrics.json              (stage 1)
reports/<run_id>/baseline/Txx/ , governed/Txx/       (stage 1 per-task A/B evidence)
```

Optional self-check:

```bash
python3 -m py_compile benchmark/*.py
```

`--mode local-model` is a documented future option (Stage 2 outlook); it is not enabled in this sprint and
falls back to `mock`.
