import importlib

from library_codex.benchmarks.profile_composition import FUNCTIONS, run_child


def test_profile_preserves_output_and_restores_functions():
    module = importlib.import_module("library_codex.fps998.Composition")
    originals = {name: getattr(module, name) for name in FUNCTIONS}
    plain = run_child(80, "plain", 92471)
    measured = run_child(80, "instrumented", 92471)
    assert plain["outputSha256"] == measured["outputSha256"]
    assert plain["inputSha256"] == measured["inputSha256"]
    assert all(getattr(module, name) is value for name, value in originals.items())
    rows = measured["functions"]
    assert rows["_butterfly"]["lengths"] == {256: 7, 512: 7}
    assert rows["_butterfly_inv"]["lengths"] == {256: 7, 512: 7}
    assert rows["_ntt_plan"]["calls"] == 2
    assert abs(sum(row["exclusiveSeconds"] for row in rows.values()) - rows["_compose_ntt"]["inclusiveSeconds"]) < 1e-6


def test_profile_small_naive_path():
    plain = run_child(2, "plain", 91)
    measured = run_child(2, "instrumented", 91)
    assert plain["outputSha256"] == measured["outputSha256"]
    assert "_butterfly" not in measured["functions"]
