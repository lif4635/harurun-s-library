import random
from pathlib import Path
import subprocess
import sys

import pytest

from library_codex.linear_algebra.Strassen import strassen_matrix_multiply
from library_codex.tools.build_library_catalog import build_standalone_code


def _naive(first, second, mod=None):
    result = [[0] * len(second[0]) for _ in first]
    for row in range(len(first)):
        for pivot in range(len(second)):
            for column in range(len(second[0])):
                result[row][column] += first[row][pivot] * second[pivot][column]
        if mod is not None:
            result[row] = [value % mod for value in result[row]]
    return result


def test_strassen_rectangular_against_naive():
    rng = random.Random(737)
    for rows, inner, columns in (
        (1, 1, 1), (3, 5, 2), (17, 13, 19), (33, 35, 31), (65, 61, 67),
        (1, 257, 1), (257, 1, 3), (3, 1, 257), (32, 32, 32)
    ):
        first = [[rng.randrange(-100, 101) for _ in range(inner)]
                 for _ in range(rows)]
        second = [[rng.randrange(-100, 101) for _ in range(columns)]
                  for _ in range(inner)]
        assert strassen_matrix_multiply(
            first, second, mod=None, threshold=8
        ) == _naive(first, second)
        assert strassen_matrix_multiply(
            first, second, mod=998244353, threshold=8
        ) == _naive(first, second, 998244353)


def test_strassen_accumulation_bounds_and_generic_moduli():
    rng = random.Random(620510)
    for mod in (1, 2, 998244353, 1 << 30, (1 << 30) + 1, (1 << 89) - 1, -101, None):
        bound = abs(mod) if mod else 10 ** 20
        for size in (7, 8, 9, 16, 17):
            first = [[rng.randrange(-bound * bound, bound * bound + 1)
                      for _ in range(size)] for _ in range(3)]
            second = [[rng.randrange(-bound * bound, bound * bound + 1)
                       for _ in range(5)] for _ in range(size)]
            saved = ([row[:] for row in first], [row[:] for row in second])
            expected = _naive(first, second, mod)
            for threshold in (8, 32):
                assert strassen_matrix_multiply(first, second, mod, threshold) == expected
            assert (first, second) == saved
            if mod:
                first = [[mod - 1] * size] * 3
                second = [[mod - 1] * 5 for _ in range(size)]
                assert strassen_matrix_multiply(first, second, mod, 32) == _naive(first, second, mod)


def test_strassen_empty_and_shapes():
    assert strassen_matrix_multiply([], []) == []
    assert strassen_matrix_multiply([[], []], []) == [[], []]
    for threshold in (0, -1):
        with pytest.raises(ValueError):
            strassen_matrix_multiply([[1]], [[1]], threshold=threshold)
    for first, second in (([[1, 2], [3]], [[1], [2]]), ([[1]], [[1], [2]]),
                          ([[1, 2]], [[1], [2, 3]])):
        with pytest.raises(ValueError):
            strassen_matrix_multiply(first, second)


def test_strassen_bundle_has_no_fps_dependency(tmp_path):
    root = Path(__file__).resolve().parents[2]
    source, dependencies = build_standalone_code(root / "linear_algebra" / "Strassen.py", root)
    assert dependencies == []
    assert "FormalPowerSeries" not in source
    script = tmp_path / "main.py"
    script.write_text(source + "\nassert strassen_matrix_multiply([[1, 2]], [[3], [4]]) == [[11]]\n",
                      encoding="utf-8")
    subprocess.run([sys.executable, "-I", str(script)], cwd=tmp_path, check=True)
