# hestiaos-benchmarks

Reproducible HestiaOS **test & benchmark harnesses** — for validation, evidence generation, and external /
playground evaluation preparation.

> This repo is **not** an edition repo and **not** a runtime deployment. Benchmarks generate **evidence
> artifacts**; they do not modify external systems.

## Role

```
- reproducible tests
- benchmarks
- validation harnesses
- evidence generation
- playground / external-validation preparation
```

## Contents

```
benchmarks/
  jupiter-dgs-stage0-stage1/   First benchmark: portable JUPITER/JSC playground prep —
                               Stage 0 environment probe + Stage 1 mock A/B DGS benchmark
                               (governed vs ungated). stdlib-only primary path.
```

## Not to be confused with

```
science-edition  -> the actual HestiaOS Science Edition (reserved; NOT this repo).
```
The benchmark here is a **harness / portability probe / DGS-vs-baseline evaluation / evidence generator** —
**not** a full Science Edition, **not** a Jülich/JUPITER-validated system or result, **not** foundation-model
training, **not** a production deployment.

## Quick pointer

See `benchmarks/jupiter-dgs-stage0-stage1/QUICKSTART.md`. Primary path is stdlib-only:

```bash
cd benchmarks/jupiter-dgs-stage0-stage1
python3 benchmark/run_stage0_environment_probe.py --out reports
python3 benchmark/run_stage1_dgs_benchmark.py --mode mock --out reports
```

## Safety

No network, no external/destructive actions, no scheduler/HPC jobs, no secrets in reports. See each
benchmark's `CLAIM_BOUNDARY.md` and the repo `SECURITY.md` / `PROVENANCE.md`.
