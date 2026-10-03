import ast
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT.parent))

import build_codon
from build_library_catalog import build_standalone_code
from library_codex.benchmarks.codon_cases import CASES, REGRESSIONS


def test_generation_is_deterministic_and_preserves_source():
    paths = [ROOT / (module + ".py") for module in build_codon.SUPPORTED]
    before = {path: path.read_bytes() for path in paths}
    for module in build_codon.SUPPORTED:
        code = build_codon.generate(module)
        assert code == build_codon.generate(module)
        assert "__slots__" not in code
        assert "from library_codex" not in code
        assert "from array" not in code
    assert before == {path: path.read_bytes() for path in paths}


def test_unknown_module_is_rejected():
    with pytest.raises(ValueError, match="not verified"):
        build_codon.generate("tree/HeavyLightDecomposition")


def test_widening_happens_before_multiplication():
    original = ast.parse("-(a * b) + c", mode="eval").body
    transformed = build_codon.wide(original)
    assert ast.unparse(transformed) == "-(Int[128](a) * Int[128](b)) + Int[128](c)"
    assert ast.unparse(original) == "-(a * b) + c"


def test_transform_only_rewrites_known_cache_get():
    source = "a = self.get(i)\nb = cache.get(i)\nc = _INVERSE_SIZE.get(i)\n"
    tree = ast.fix_missing_locations(build_codon.CodonTransformer(False).visit(ast.parse(source)))
    result = ast.unparse(tree)
    assert "self.get(i)" in result
    assert "cache.get(i)" in result
    assert "i in _INVERSE_SIZE" in result


def test_constructor_change_fails_closed():
    source = "class SegTree:\n def __init__(self, values):\n  self.n = len(values)\n"
    with pytest.raises(ValueError, match="constructor changed"):
        build_codon.CodonTransformer(False).visit(ast.parse(source))


def test_output_does_not_replace_canonical_files(tmp_path):
    for path in (build_codon.HEADER, ROOT / "fenwick_tree/BIT.py", ROOT / "tools/build_codon.py"):
        with pytest.raises(ValueError, match="generated"):
            build_codon.validate_output(path)
    with pytest.raises(ValueError, match="solution"):
        build_codon.validate_output(tmp_path / "Main.py", tmp_path / "Main.py")
    build_codon.validate_output(tmp_path / "Main.py")


def test_atomic_write_preserves_previous_file_on_failure(tmp_path, monkeypatch):
    path = tmp_path / "Main.py"
    build_codon.atomic_write(path, "old")

    def fail(*args):
        raise OSError("injected failure")

    monkeypatch.setattr(build_codon.os, "replace", fail)
    with pytest.raises(OSError, match="injected"):
        build_codon.atomic_write(path, "new")
    assert path.read_text() == "old"
    assert list(tmp_path.iterdir()) == [path]


@pytest.fixture(scope="module")
def codon():
    executable = shutil.which("codon")
    if executable is None:
        pytest.skip("Codon is not installed; native compilation was not tested")
    version = subprocess.check_output([executable, "--version"], text=True).strip()
    if version != "0.19.3":
        pytest.skip("native tests require AtCoder's Codon 0.19.3")
    return executable


def compile_run(codon, path, source, stdin=""):
    path.write_text(source, encoding="utf-8")
    executable = path.with_suffix(".out")
    build = subprocess.run([codon, "build", "--release", "-o", str(executable), str(path)], capture_output=True, text=True, timeout=120)
    assert build.returncode == 0, build.stdout + build.stderr
    result = subprocess.run([str(executable)], input=stdin, capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stdout + result.stderr
    return result.stdout


@pytest.mark.parametrize("module", build_codon.SUPPORTED)
def test_native_matches_canonical(module, codon, tmp_path):
    original, _ = build_standalone_code(ROOT / (module + ".py"), ROOT)
    solver = CASES[module] + REGRESSIONS[module]
    reference = tmp_path / "reference.py"
    reference.write_text("import sys\n" + original + "\n" + solver, encoding="utf-8")
    expected = subprocess.check_output([sys.executable, str(reference)], input="513\n", text=True, timeout=60)
    actual = compile_run(codon, tmp_path / "native.py", build_codon.generate(module) + "\n" + solver, "513\n")
    assert actual == expected


def test_header_integer_boundaries_and_input(codon, tmp_path):
    solver = '''
for value in [0, 1, -1, 2, -7, 9223372036854775807, -9223372036854775807-1]:
    print(value.bit_length(), value.bit_count())
    for divisor in [-998244353, -3, 3, 998244353]:
        print(value // divisor, value % divisor)
for base in [-9223372036854775807-1, -17, 0, 1, 17, 9223372036854775807]:
    for exponent in [-2, -1, 0, 1, 100]:
        for modulus in [-9223372036854775807-1, -998244353, -1, 1, 998244353, 9223372036854775783]:
            try:
                print(pow(base, exponent, modulus))
            except ValueError:
                print("ValueError")
for i in range(5):
    print(repr(sys.stdin.readline()))
'''
    reference = tmp_path / "reference.py"
    reference.write_text("import sys\n" + solver, encoding="utf-8")
    stdin = "one\n\nthree\n"
    expected = subprocess.check_output([sys.executable, str(reference)], input=stdin, text=True, timeout=30)
    native = build_codon.HEADER.read_text(encoding="utf-8") + solver.replace("pow(base,", "_codon_pow(base,")
    assert compile_run(codon, tmp_path / "header.py", native, stdin) == expected
