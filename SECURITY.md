# Security Policy

## Scope

Private research / benchmark repository (`hestiaos-benchmarks`). Contains reproducible test and benchmark
harnesses (documentation, stdlib-only Python scripts, optional container recipe, optional content-only
provenance library extract). It executes no real builds, makes no network calls, and starts no scheduler/HPC
jobs.

## Status

This repository is **not yet public-ready**. A final security reporting channel will be defined **before any
public release**. Until then there is no published public disclosure channel.

## Reporting (pre-public)

While private, handle security-relevant findings directly with the repository owner via the existing private
development workflow. A formal public channel will be added here prior to public release.

## Handling of sensitive data

```
- No secrets, tokens, private keys, .env files, internal hostnames, or private IPs may be committed.
- Do NOT paste credentials or private hostnames into issues or reports.
- Benchmark runs write only into <benchmark>/reports/<run_id>/ and must not contain secrets; redact before
  sharing externally.
```
