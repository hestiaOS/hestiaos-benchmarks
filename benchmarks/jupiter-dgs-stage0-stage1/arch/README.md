# Arch / archiso path (optional, tertiary)

For the Arch-affine research / HPC crowd. This is an **optional** context note, **not** a required path and
**not** part of Stage 0/1.

## Context

- An older HestiaOS Science Edition existed as a separate **archiso ISO profile** (`archiso-science`, v1.0.0,
  2026-05-21) — a separate lineage from the current kernel line.
- **This demo repo ships no ISO and no qcow2.** No image artifacts are included or built here.

## What Arch users should do

```
1. Just run the stdlib-only kit directly — Arch ships Python 3:
     python3 benchmark/run_stage0_environment_probe.py --out reports
     python3 benchmark/run_stage1_dgs_benchmark.py --mode mock --out reports
2. (Optional) Use the container path (container/README.md) via Podman (Arch ships Podman well).
3. (Optional, advanced) The richer provenance layer lives in optional_stage2_science_trace/ (stdlib only).
```

## Explicitly NOT in scope here

```
- No archiso/ISO build required or shipped.
- No root/container build required for Stage 0/1.
- No Jülich/JUPITER validation claim.
- The old archiso-science profile stays in its own repo; only a content-only extract of its science_trace
  library is included as the optional Stage-2 layer.
```
