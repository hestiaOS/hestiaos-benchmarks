#!/usr/bin/env python3
"""Offline test runner for environments without pytest (no network).

In CI with pytest installed, prefer:  python -m pytest -q
This runner registers a minimal in-memory `pytest` shim ONLY if the real package
is absent, so it never shadows a real installation, and it returns a nonzero exit
code on failure.
"""
import sys, math, types, traceback

try:
    import pytest  # noqa: F401  (use the real thing if present)
except ImportError:
    shim = types.ModuleType("pytest")

    class approx:
        def __init__(self, e, rel=None, abs=None): self.e, self.rel, self.abs = e, rel, abs
        def __eq__(self, o):
            a = self.abs if self.abs is not None else 1e-6
            r = self.rel if self.rel is not None else 1e-6
            try:
                return math.isclose(float(o), float(self.e), rel_tol=r, abs_tol=a)
            except TypeError:
                return all(approx(e, self.rel, self.abs) == x for e, x in zip(self.e, o))

    class _Raises:
        def __init__(self, exc): self.exc = exc
        def __enter__(self): return self
        def __exit__(self, et, ev, tb): return et is not None and issubclass(et, self.exc)

    shim.approx = approx
    shim.raises = lambda exc: _Raises(exc)
    shim.main = lambda *a, **k: 0
    sys.modules["pytest"] = shim

import test_collapse_rank as T  # noqa: E402

tests = sorted(n for n in dir(T) if n.startswith("test_"))
passed, failed = 0, []
for n in tests:
    try:
        getattr(T, n)(); print(f"PASS  {n}"); passed += 1
    except Exception as e:
        failed.append(n); print(f"FAIL  {n}: {e}"); traceback.print_exc()
print(f"\n==== {passed}/{len(tests)} passed, {len(failed)} failed ====")
raise SystemExit(1 if failed else 0)
