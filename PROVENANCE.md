# Provenance

## Origin

Fresh-root clean-room projection. **No legacy git history.**

```
Source        : vetted local clean-room kit
Placement     : benchmarks/jupiter-dgs-stage0-stage1/
Stage 0/1     : newly built for this kit (stdlib only).
optional Stage 2: content-only extract of HestiaOS Science Edition v1.0.0 —
                 library + demo + configs. No ISO, no build scripts, no pycache, no history.
container/, arch/: optional run paths (Podman/Docker; Arch context note).
```

## Boundaries

```
- No old git history imported.
- No ISO / qcow2 / image artifacts shipped or built.
- No Jülich / JUPITER validation claim (see the benchmark's CLAIM_BOUNDARY.md).
- No foundation-model training, no production claim.
```

## HestiaOS repo references (context only, NOT a build dependency)

```
hestiaos-core              (governance kernel; context only, not a build target)
edition-build-pipeline     (component lock / manifest / validation; context only)
hestiaos-community-edition (clean-room composition; context only)
science-edition            (reserved for the actual Science Edition; NOT this repo)
```
This repo is self-contained: benchmarks do not import from or modify those repos at runtime.
