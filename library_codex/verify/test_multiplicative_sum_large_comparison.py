import hashlib
from pathlib import Path

from library_codex.benchmarks import multiplicative_sum_large_comparison as comparison
from library_codex.benchmarks import multiplicative_sum_comparison as run_comparison


def test_baseline_retains_helpers_and_module_globals(monkeypatch):
    path = Path(comparison.__file__).parents[1] / "number_theory/MultiplicativeFunctions.py"
    source = path.read_text()
    monkeypatch.setattr(comparison.subprocess, "check_output", lambda *a, **k: source)
    cls, digest = comparison.baseline("test-revision")
    assert digest == hashlib.sha256(source.encode()).hexdigest()
    assert cls.run.__globals__["__name__"] == "multiplicative_baseline"
    assert cls.run.__globals__["_small_quotient"](10, 3) == 3
    engine = cls(1000, 469762049)
    prefix = engine.prime_count_table()
    assert engine.run(prefix, lambda p, e: 1) == 1000
    assert engine.prime_sum_table(7, 6) == comparison.MultiplicativePrefixSum(1000, 469762049).prime_sum_table(7, 6)


def test_run_baseline_uses_module_globals(monkeypatch):
    source = "class MultiplicativePrefixSum:\n    def run(self, values, callback):\n        return sum(values)\n"
    monkeypatch.setattr(run_comparison.subprocess, "check_output", lambda *a, **k: source)
    run, digest = run_comparison.baseline("test-revision")
    assert run.__globals__["__name__"] == "multiplicative_run_baseline"
    assert digest == hashlib.sha256(source.encode()).hexdigest()
    assert run(None, [2, 3, 7], None) == 12
