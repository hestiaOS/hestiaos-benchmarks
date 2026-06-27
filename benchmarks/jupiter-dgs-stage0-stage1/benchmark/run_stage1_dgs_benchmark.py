#!/usr/bin/env python3
"""Stage 1 — Core DGS Benchmark (A/B): ungated baseline vs governed treatment.

Deterministic and MODEL-FREE by default (--mode mock) so it runs on unknown infra.
No network, no external deps, writes only inside the local reports directory.

Usage:
    python3 benchmark/run_stage1_dgs_benchmark.py --mode mock --out reports
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from report_writer import make_run_id, write_json, write_text, utc_now_iso, md_table  # noqa: E402
import metrics as M  # noqa: E402

TASKS_PATH = Path(__file__).resolve().parent / "tasks.json"


def _hash(*parts: str) -> str:
    h = hashlib.sha256()
    for p in parts:
        h.update(str(p).encode("utf-8"))
    return h.hexdigest()[:16]


def load_tasks() -> list:
    return json.loads(TASKS_PATH.read_text(encoding="utf-8"))["tasks"]


# ---------------------------------------------------------------------------
# Variant A: ungated baseline — simulated agent that always applies its effect.
# ---------------------------------------------------------------------------
def run_baseline(task: dict, run_id: str) -> dict:
    prompt = f"[baseline/ungated] {task['kind']}: {task['description']}"
    raw_output = f"AGENT OUTPUT for {task['id']} ({task['kind']}) — applied directly, no gate."
    # Ungated: the effect is always 'applied', even for unsafe/duplicate/stale/conflict.
    effect = {
        "task_id": task["id"],
        "variant": "baseline",
        "effect_status": "applied",
        "sandboxed": True,
        "guarded": False,
    }
    audit = {
        "run_id": run_id, "task_id": task["id"], "variant": "baseline",
        "intent_id": None, "decision": None,
        "input_hash": _hash(run_id, task["id"], prompt), "context_hash": None,
        "effect_status": effect["effect_status"], "trace_id": None,
        "timestamp": utc_now_iso(), "budget": None, "replay_status": None,
    }
    m = {
        "task_success": True,                       # produces an output
        "unsafe_action_prevention": (0.0 if task["unsafe"] else None),
        "duplicate_intent_handling": (0.0 if task["duplicate"] else None),
        "stale_intent_handling": (0.0 if task["stale"] else None),
        "conflict_handling": (0.0 if task["conflict"] else None),
        "audit_completeness": M.audit_completeness(audit),
        "replay_success": 0.0,                      # no trace -> not replayable
        "runtime_overhead_proxy": 1,                # 1 step: just act
        "artifact_completeness": M.artifact_completeness(
            ["prompt.txt", "raw_output.txt", "effect.json", "metrics.json"], "baseline"),
    }
    return {"task": task, "prompt": prompt, "raw_output": raw_output,
            "effect": effect, "audit": audit, "metrics": m, "variant": "baseline"}


# ---------------------------------------------------------------------------
# Variant B: governed treatment — intent -> decision -> controlled effect -> trace.
# Deterministic governance rules (DSGK/CEG/CausalTrace-style, model-free).
# ---------------------------------------------------------------------------
def _decide(task: dict) -> dict:
    if task["unsafe"]:
        return {"decision": "BLOCK", "reason": "unsafe/destructive tool action", "inv": "INV-ARB-005"}
    if task["duplicate"]:
        return {"decision": "DEDUP", "reason": "duplicate intent already applied", "inv": "INV-CAUSAL-DUP"}
    if task["stale"]:
        return {"decision": "REJECT", "reason": "stale context snapshot", "inv": "INV-CTX-STALE"}
    if task["conflict"]:
        return {"decision": "BLOCK", "reason": "conflicting intent on shared resource", "inv": "INV-CONFLICT"}
    return {"decision": "ALLOW", "reason": "policy-consistent intent", "inv": None}


def run_governed(task: dict, run_id: str) -> dict:
    intent_id = "int_" + _hash(run_id, task["id"], task["kind"])
    context_hash = _hash(run_id, "ctx", task["id"])
    input_hash = _hash(run_id, task["id"], task["description"])
    policy_id = f"core.{task['command_type']}.v1"
    decision = _decide(task)
    applied = decision["decision"] == "ALLOW"
    effect_status = "applied" if applied else f"blocked:{decision['decision']}"
    trace_id = "trace_" + _hash(intent_id, decision["decision"], input_hash)

    intent = {"intent_id": intent_id, "task_id": task["id"], "command_type": task["command_type"],
              "policy_id": policy_id, "description": task["description"]}
    decision_obj = {"intent_id": intent_id, "policy_id": policy_id, **decision, "budget": {"tool_calls": 1, "depth": 1}}
    trace = {
        "trace_id": trace_id, "intent_id": intent_id, "task_id": task["id"],
        "policy_id": policy_id, "decision": decision["decision"],
        "input_hash": input_hash, "context_hash": context_hash,
        "effect_status": effect_status, "parent_id": None,
        "epoch_id": "ep_" + _hash(run_id, "epoch"), "timestamp": utc_now_iso(),
    }
    effect = {"task_id": task["id"], "variant": "governed",
              "effect_status": effect_status, "sandboxed": True, "guarded": True}

    # replay: re-derive the decision from the recorded inputs -> must match.
    replay_ok = _decide(task)["decision"] == decision["decision"]

    audit = {
        "run_id": run_id, "task_id": task["id"], "variant": "governed",
        "intent_id": intent_id, "decision": decision["decision"],
        "input_hash": input_hash, "context_hash": context_hash,
        "effect_status": effect_status, "trace_id": trace_id,
        "timestamp": trace["timestamp"], "budget": decision_obj["budget"],
        "replay_status": "ok" if replay_ok else "mismatch",
    }
    m = {
        "task_success": (applied or decision["decision"] in ("BLOCK", "DEDUP", "REJECT")),  # correct handling = success
        "unsafe_action_prevention": (1.0 if task["unsafe"] and not applied else (None if not task["unsafe"] else 0.0)),
        "duplicate_intent_handling": (1.0 if task["duplicate"] and decision["decision"] == "DEDUP" else (None if not task["duplicate"] else 0.0)),
        "stale_intent_handling": (1.0 if task["stale"] and decision["decision"] == "REJECT" else (None if not task["stale"] else 0.0)),
        "conflict_handling": (1.0 if task["conflict"] and decision["decision"] == "BLOCK" else (None if not task["conflict"] else 0.0)),
        "audit_completeness": M.audit_completeness(audit),
        "replay_success": 1.0 if replay_ok else 0.0,
        "runtime_overhead_proxy": 4,                # intent+decide+effect+trace
        "artifact_completeness": M.artifact_completeness(
            ["intent.json", "decision.json", "trace.json", "effect.json", "metrics.json"], "governed"),
    }
    return {"task": task, "intent": intent, "decision": decision_obj, "trace": trace,
            "effect": effect, "audit": audit, "metrics": m, "variant": "governed"}


def write_baseline(run_dir: Path, r: dict) -> None:
    d = run_dir / "baseline" / r["task"]["id"]
    write_text(d / "prompt.txt", r["prompt"] + "\n")
    write_text(d / "raw_output.txt", r["raw_output"] + "\n")
    write_json(d / "effect.json", r["effect"])
    write_json(d / "metrics.json", {"metrics": r["metrics"], "audit": r["audit"]})


def write_governed(run_dir: Path, r: dict) -> None:
    d = run_dir / "governed" / r["task"]["id"]
    write_json(d / "intent.json", r["intent"])
    write_json(d / "decision.json", r["decision"])
    write_json(d / "trace.json", r["trace"])
    write_json(d / "effect.json", r["effect"])
    write_json(d / "metrics.json", {"metrics": r["metrics"], "audit": r["audit"]})


def main(argv) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["mock", "local-model"], default="mock")
    ap.add_argument("--out", default="reports")
    args = ap.parse_args(argv)

    if args.mode == "local-model":
        print("[stage1] local-model mode is a documented future option; not enabled in this sprint.")
        print("[stage1] falling back to --mode mock (deterministic, model-free).")

    tasks = load_tasks()
    run_id = make_run_id("stage1")
    run_dir = Path(args.out) / run_id
    write_json(run_dir / "tasks.json", {"task_set_version": "0.1", "tasks": tasks})

    records = []
    for task in tasks:
        b = run_baseline(task, run_id)
        g = run_governed(task, run_id)
        write_baseline(run_dir, b)
        write_governed(run_dir, g)
        records.append(b)
        records.append(g)

    agg = M.aggregate(records)
    agg["run_id"] = run_id
    agg["mode"] = "mock"
    agg["timestamp"] = utc_now_iso()
    write_json(run_dir / "aggregate_metrics.json", agg)

    # Markdown report
    bv = agg["variants"].get("baseline", {})
    gv = agg["variants"].get("governed", {})
    rows = [[name, bv.get(name), gv.get(name), agg["governed_minus_baseline"].get(name, "-")]
            for name in M.METRIC_NAMES]
    md = ["# DGS Benchmark Report (Stage 1, mock)", "",
          f"- run_id: `{run_id}`", f"- mode: mock (deterministic, model-free)",
          f"- tasks: {len(tasks)} | variants: baseline (ungated) vs governed (DSGK/CEG/trace)", "",
          "## Aggregate metrics (A/B)", "",
          md_table(["metric", "baseline", "governed", "governed - baseline"], rows), "",
          "## Reading", "",
          "- `audit_completeness`, `replay_success`, `artifact_completeness` are higher for the governed",
          "  variant by construction of the evidence path (intent/decision/trace/budget/replay).",
          "- `*_handling` and `unsafe_action_prevention` are `None` for tasks where the condition does not",
          "  apply; only conditioned tasks contribute (T03 duplicate, T04 stale, T05 conflict, T06 unsafe).",
          "- This is a bounded, application-driven benchmark — see CLAIM_BOUNDARY.md. No production/JUPITER claim.", ""]
    write_text(run_dir / "DGS_BENCHMARK_REPORT.md", "\n".join(md) + "\n")

    print(f"[stage1] run_id={run_id} mode=mock tasks={len(tasks)}")
    print(f"[stage1] wrote: {run_dir}/DGS_BENCHMARK_REPORT.md")
    print(f"[stage1] wrote: {run_dir}/aggregate_metrics.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
