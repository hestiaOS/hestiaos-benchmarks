# Expected Report Structure

After running both stages, `reports/` looks like this:

```
reports/
  stage0_<ts>_<id>/
    run_manifest.json
    environment_profile.json
    PLAYGROUND_ENVIRONMENT_PROFILE.md
    PORTABILITY_GAP_REPORT.md
  stage1_<ts>_<id>/
    tasks.json
    aggregate_metrics.json
    DGS_BENCHMARK_REPORT.md
    baseline/
      T01/ ... T08/
        prompt.txt
        raw_output.txt
        effect.json
        metrics.json
    governed/
      T01/ ... T08/
        intent.json
        decision.json
        trace.json
        effect.json
        metrics.json
```

## aggregate_metrics.json (shape)

```json
{
  "run_id": "stage1_...",
  "mode": "mock",
  "metric_names": ["task_success", "..."],
  "variants": {
    "baseline": {"n_tasks": 8, "audit_completeness": 0.5, "replay_success": 0.0, "...": "..."},
    "governed": {"n_tasks": 8, "audit_completeness": 1.0, "replay_success": 1.0, "...": "..."}
  },
  "governed_minus_baseline": {"audit_completeness": 0.5, "replay_success": 1.0, "...": "..."}
}
```

## Illustrative result (from a local mock run)

| metric | baseline | governed | delta |
| --- | --- | --- | --- |
| audit_completeness | 0.5 | 1.0 | +0.5 |
| replay_success | 0.0 | 1.0 | +1.0 |
| unsafe_action_prevention | 0.0 | 1.0 | +1.0 |
| duplicate_intent_handling | 0.0 | 1.0 | +1.0 |
| stale_intent_handling | 0.0 | 1.0 | +1.0 |
| conflict_handling | 0.0 | 1.0 | +1.0 |
| runtime_overhead_proxy | 1 | 4 | +3 |

Note: `*_handling` / `unsafe_action_prevention` are computed only on the conditioned tasks
(T03 duplicate, T04 stale, T05 conflict, T06 unsafe); other tasks contribute `None`.
Numbers are illustrative of the mock harness, not a production or JUPITER claim.
