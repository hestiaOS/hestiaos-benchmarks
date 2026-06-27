#!/usr/bin/env python3
"""Stage 0 — Portability & Environment Baseline probe.

READ-ONLY. No network checks, no GPU benchmarks, no scheduler jobs. Only records a
portability profile and writes into the local reports directory.

Usage:
    python3 benchmark/run_stage0_environment_probe.py --out reports
"""
from __future__ import annotations

import argparse
import importlib.util
import os
import platform
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from report_writer import make_run_id, write_json, write_text, utc_now_iso, md_table  # noqa: E402

# Environment variables we are allowed to record (no secrets).
ENV_ALLOWLIST = ["PATH", "PYTHONPATH", "OLLAMA_MODEL"]
# Container / scheduler hints (presence + value, none are secret).
CONTAINER_HINTS = [
    "APPTAINER_NAME", "SINGULARITY_NAME",
    "SLURM_JOB_ID", "SLURM_CLUSTER_NAME", "CUDA_VISIBLE_DEVICES",
]
# Local package import checks (presence only; no execution side effects).
IMPORT_CHECKS = ["json", "hashlib", "dataclasses", "pathlib"]


def _disk_free_gb(path: Path) -> float:
    try:
        usage = shutil.disk_usage(str(path))
        return round(usage.free / (1024 ** 3), 2)
    except OSError:
        return -1.0


def _can_write(path: Path) -> bool:
    try:
        path.mkdir(parents=True, exist_ok=True)
        probe = path / ".write_probe"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
        return True
    except OSError:
        return False


def collect_profile(out_root: Path) -> dict:
    cwd = Path.cwd()
    env = {k: os.environ[k] for k in ENV_ALLOWLIST if k in os.environ}
    hints = {k: os.environ.get(k) for k in CONTAINER_HINTS if k in os.environ}
    imports = {}
    for mod in IMPORT_CHECKS:
        imports[mod] = importlib.util.find_spec(mod) is not None
    return {
        "stage": 0,
        "timestamp": utc_now_iso(),
        "python_version": sys.version.split()[0],
        "python_implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "os": os.name,
        "working_directory": str(cwd),
        "disk_free_gb_for_cwd": _disk_free_gb(cwd),
        "disk_free_gb_for_out": _disk_free_gb(out_root),
        "env_allowlist": env,
        "container_scheduler_hints": hints,
        "git_available": shutil.which("git") is not None,
        "import_checks": imports,
        "reports_dir_writable": _can_write(out_root),
        "notes": "read-only probe; no network, no GPU benchmark, no scheduler jobs",
    }


def portability_gaps(profile: dict) -> list:
    gaps = []
    if not profile["reports_dir_writable"]:
        gaps.append("reports dir NOT writable -> cannot persist evidence")
    if profile["disk_free_gb_for_out"] >= 0 and profile["disk_free_gb_for_out"] < 1:
        gaps.append("low disk space (<1 GB) at output path")
    if not profile["git_available"]:
        gaps.append("git not available (provenance capture limited)")
    if not all(profile["import_checks"].values()):
        missing = [m for m, ok in profile["import_checks"].items() if not ok]
        gaps.append(f"missing stdlib import(s): {missing}")
    if not profile["container_scheduler_hints"]:
        gaps.append("no container/scheduler hints -> assume bare/unknown environment")
    if "OLLAMA_MODEL" not in profile["env_allowlist"]:
        gaps.append("OLLAMA_MODEL not set -> local-model mode unavailable; use --mode mock")
    return gaps


def main(argv) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="reports")
    args = ap.parse_args(argv)

    out_root = Path(args.out)
    run_id = make_run_id("stage0")
    run_dir = out_root / run_id

    profile = collect_profile(out_root)
    gaps = portability_gaps(profile)

    write_json(run_dir / "run_manifest.json", {
        "run_id": run_id, "stage": 0, "timestamp": profile["timestamp"],
        "artifacts": ["PLAYGROUND_ENVIRONMENT_PROFILE.md", "PORTABILITY_GAP_REPORT.md", "run_manifest.json"],
    })

    prof_md = ["# Playground Environment Profile", "",
               f"- run_id: `{run_id}`", f"- timestamp: {profile['timestamp']}", ""]
    prof_md.append(md_table(["key", "value"], [
        ["python_version", profile["python_version"]],
        ["python_implementation", profile["python_implementation"]],
        ["platform", profile["platform"]],
        ["machine", profile["machine"]],
        ["working_directory", profile["working_directory"]],
        ["disk_free_gb_for_out", profile["disk_free_gb_for_out"]],
        ["git_available", profile["git_available"]],
        ["reports_dir_writable", profile["reports_dir_writable"]],
    ]))
    env_lines = [f"{k}={v}" for k, v in profile["env_allowlist"].items()] or ["(none)"]
    hint_lines = [f"{k}={v}" for k, v in profile["container_scheduler_hints"].items()] or ["(none detected)"]
    import_lines = [f"{m}: {ok}" for m, ok in profile["import_checks"].items()]
    prof_md += ["", "## Env allowlist", "```", *env_lines, "```"]
    prof_md += ["", "## Container / scheduler hints", "```", *hint_lines, "```"]
    prof_md += ["", "## Import checks", "```", *import_lines, "```"]
    write_text(run_dir / "PLAYGROUND_ENVIRONMENT_PROFILE.md", "\n".join(prof_md) + "\n")

    gap_md = ["# Portability Gap Report", "", f"- run_id: `{run_id}`", "",
              "## Detected gaps / assumptions", ""]
    gap_md += ([f"- {g}" for g in gaps] if gaps else ["- none detected"])
    gap_md += ["", "## Go / No-Go for Stage 1 (mock)",
               "Stage 1 mock has NO external dependencies; it can run whenever the reports dir is writable.",
               f"reports_dir_writable = {profile['reports_dir_writable']}",
               "", "Recommendation: " +
               ("GO for Stage 1 mock" if profile["reports_dir_writable"] else "NO-GO until reports dir is writable")]
    write_text(run_dir / "PORTABILITY_GAP_REPORT.md", "\n".join(gap_md) + "\n")
    write_json(run_dir / "environment_profile.json", profile)

    print(f"[stage0] run_id={run_id}")
    print(f"[stage0] wrote: {run_dir}/PLAYGROUND_ENVIRONMENT_PROFILE.md")
    print(f"[stage0] wrote: {run_dir}/PORTABILITY_GAP_REPORT.md")
    print(f"[stage0] gaps: {len(gaps)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
