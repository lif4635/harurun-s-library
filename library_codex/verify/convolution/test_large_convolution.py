from array import array
import ast
import importlib
import random
import subprocess
import sys

from library_codex.convolution.LargeConvolution import _multiply_blocks, _multiply_four_lanes, multiply
from library_codex.convolution.NTT998 import MOD


def naive(first, second):
    if not first or not second:
        return []
    result = [0] * (len(first) + len(second) - 1)
    for i, a in enumerate(first):
        for j, b in enumerate(second):
            result[i + j] = (result[i + j] + a * b) % MOD
    return result


def test_boundaries():
    for a, b in (([], []), ([], [1]), ([1], []), ([0], [5]), ([-2], [MOD + 3])):
        assert multiply(a, b) == naive(a, b)
    assert multiply((1, 2), array("I", [3, 4])) == [3, 10, 8]


def test_block_boundaries_and_random():
    rng = random.Random(20261020)
    for block in (1, 2, 4, 8, 16, 64):
        lengths = sorted({1, block, block + 1, 2 * block - 1, 2 * block, 3 * block + 1})
        for n in lengths:
            for m in lengths:
                a = [rng.randrange(-2 * MOD, 3 * MOD) for _ in range(n)]
                b = [rng.randrange(-2 * MOD, 3 * MOD) for _ in range(m)]
                before_a, before_b = a[:], b[:]
                assert _multiply_blocks(a, b, block) == naive(a, b)
                assert a == before_a and b == before_b
        for n in lengths:
            a = [rng.randrange(MOD) for _ in range(n)]
            assert _multiply_blocks(a, a, block) == naive(a, a)
            assert _multiply_blocks([0] * n, a, block) == [0] * (2 * n - 1)


def test_transform_reuse(monkeypatch):
    module = importlib.import_module("library_codex.convolution.LargeConvolution")
    forward, inverse = module._butterfly, module._butterfly_inv
    counts = [0, 0]

    def count_forward(a):
        counts[0] += 1
        return forward(a)

    def count_inverse(a):
        counts[1] += 1
        return inverse(a)

    monkeypatch.setattr(module, "_butterfly", count_forward)
    monkeypatch.setattr(module, "_butterfly_inv", count_inverse)
    a, b = list(range(25)), list(range(19))
    assert _multiply_blocks(a, b, 8) == naive(a, b)
    assert counts == [7, 6]
    counts[:] = [0, 0]
    assert _multiply_blocks(a, a, 8) == naive(a, a)
    assert counts == [4, 7]


def test_public_large_dispatch(monkeypatch):
    module = importlib.import_module("library_codex.convolution.LargeConvolution")
    calls = []

    class Sized:
        def __init__(self, n):
            self.n = n

        def __len__(self):
            return self.n

    def record(a, b, block):
        calls.append((len(a), len(b), block))
        return calls[-1]

    monkeypatch.setattr(module, "_multiply_blocks", record)
    monkeypatch.setattr(module, "_multiply_four_lanes", record)
    assert multiply(Sized(1 << 23), Sized(65)) == (1 << 23, 65, 128)
    assert multiply(Sized(1 << 24), Sized(1 << 24)) == (1 << 24, 1 << 24, 1 << 23)
    assert multiply(Sized(1 << 23), Sized((1 << 23) + 1)) == (1 << 23, (1 << 23) + 1, 1 << 22)
    assert multiply(Sized((1 << 24) + 1), Sized(1 << 24)) == ((1 << 24) + 1, 1 << 24, 1 << 23)
    assert multiply(Sized((1 << 24) + 1), Sized((1 << 24) + 1)) == ((1 << 24) + 1, (1 << 24) + 1, 1 << 22)


def test_four_lanes_random_boundaries():
    rng = random.Random(57291)
    for size in (1, 2, 4, 8, 16, 64):
        for _ in range(30):
            n = rng.randrange(1, 4 * size + 1)
            m = rng.randrange(1, 4 * size - n + 2)
            a = [rng.randrange(-MOD, 2 * MOD) for _ in range(n)]
            b = [rng.randrange(-MOD, 2 * MOD) for _ in range(m)]
            saved = a[:], b[:]
            assert _multiply_four_lanes(a, b, size) == naive(a, b)
            assert (a, b) == saved
        a = [rng.randrange(MOD) for _ in range(2 * size)]
        assert _multiply_four_lanes(a, a, size) == naive(a, a)
        assert _multiply_four_lanes([0] * len(a), a, size) == [0] * (2 * len(a) - 1)


def test_four_lanes_transform_counts(monkeypatch):
    module = importlib.import_module("library_codex.convolution.LargeConvolution")
    forward, inverse = module._butterfly, module._butterfly_inv
    counts = [0, 0]

    def count_forward(values):
        counts[0] += 1
        return forward(values)

    def count_inverse(values):
        counts[1] += 1
        return inverse(values)

    monkeypatch.setattr(module, "_butterfly", count_forward)
    monkeypatch.setattr(module, "_butterfly_inv", count_inverse)
    a, b = list(range(15)), list(range(17))
    assert _multiply_four_lanes(a, b, 8) == naive(a, b)
    assert counts == [8, 4]
    counts[:] = [0, 0]
    assert _multiply_four_lanes(a, a, 8) == naive(a, a)
    assert counts == [4, 4]


def test_standalone(tmp_path):
    from library_codex.tools.build_library_catalog import ROOT, build_standalone_code

    source, _ = build_standalone_code(ROOT / "convolution/LargeConvolution.py", ROOT)
    block_name = next(node.name for node in ast.parse(source).body
                      if isinstance(node, ast.FunctionDef) and node.name.endswith("multiply_blocks"))
    lane_name = next(node.name for node in ast.parse(source).body
                     if isinstance(node, ast.FunctionDef) and node.name.endswith("multiply_four_lanes"))
    script = tmp_path / "main.py"
    script.write_text(source + "\nassert multiply([1, 2], [3, 4]) == [3, 10, 8]\n"
                      f"assert {block_name}([1] * 25, [1] * 19, 8) == "
                      "[min(i + 1, 19, 43 - i) for i in range(43)]\n"
                      f"assert {lane_name}([1] * 25, [1] * 19, 16) == "
                      "[min(i + 1, 19, 43 - i) for i in range(43)]\n", encoding="utf-8")
    subprocess.run([sys.executable, "-I", str(script)], cwd=tmp_path, check=True, timeout=30)


def test_driver_chunked_input():
    import importlib.util
    import io
    from pathlib import Path
    import pytest

    path = Path(__file__).resolve().parents[3] / "verify/library_checker/drivers/convolution_mod_large.py"
    spec = importlib.util.spec_from_file_location("large_driver", path)
    driver = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(driver)

    class Chunked(io.BytesIO):
        def read(self, n):
            return super().read(min(n, 7))

    values = [0, 998244352, 123456789, 1, 42] * 11
    for ending in (b"", b"\n", b" \r\n"):
        data = b" \t".join(str(x).encode() for x in values) + ending
        assert list(driver.read_coefficients(Chunked(data), len(values))) == values
    with pytest.raises(ValueError):
        driver.read_coefficients(Chunked(b"1 2"), 3)
