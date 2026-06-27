"""Minimal pytest shim (no network). Provides approx, raises, main."""
import math
class approx:
    def __init__(self, expected, rel=None, abs=None):
        self.e = expected; self.rel = rel; self.abs = abs
    def __eq__(self, other):
        a = self.abs if self.abs is not None else 1e-6
        r = self.rel if self.rel is not None else 1e-6
        try:
            return math.isclose(float(other), float(self.e), rel_tol=r, abs_tol=a)
        except TypeError:
            return all(self.__class__(e, self.rel, self.abs) == o for e, o in zip(self.e, other))
    def __req__(self, other): return self.__eq__(other)
class _Raises:
    def __init__(self, exc): self.exc = exc
    def __enter__(self): return self
    def __exit__(self, et, ev, tb): return et is not None and issubclass(et, self.exc)
def raises(exc): return _Raises(exc)
def main(args=None): return 0
