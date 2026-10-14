from itertools import product
import json
from pathlib import Path
import random
import re

import pytest

from library_codex.linear_algebra.Adjugate import adjugate
from library_codex.linear_algebra.Matrix import matrix_determinant, matrix_multiply


def oracle(matrix, mod):
    n = len(matrix)
    return [
        [
            (-1 if (i + j) & 1 else 1)
            * matrix_determinant(
                [row[:i] + row[i + 1:] for k, row in enumerate(matrix) if k != j],
                mod,
            ) % mod
            for j in range(n)
        ]
        for i in range(n)
    ]


def test_adjugate_exhaustive():
    for mod in (2, 3, 5):
        for entries in product(range(mod), repeat=4):
            a = [list(entries[:2]), list(entries[2:])]
            assert adjugate(a, mod) == oracle(a, mod)


def test_adjugate_all_ranks():
    rng = random.Random(10471)
    for mod in (2, 3, 101, 998244353):
        for n in range(1, 8):
            for rank in range(n + 1):
                for _ in range(6):
                    a = [[int(i == j and i < rank) for j in range(n)] for i in range(n)]
                    for _ in range(n * 4):
                        i, j = rng.randrange(n), rng.randrange(n)
                        if i != j:
                            scale = rng.randrange(mod)
                            a[i] = [(x + scale * y) % mod for x, y in zip(a[i], a[j])]
                            for row in a:
                                row[i] = (row[i] + scale * row[j]) % mod
                        a[i], a[j] = a[j], a[i]
                    saved = [row[:] for row in a]
                    result = adjugate(a, mod)
                    assert result == oracle(a, mod)
                    assert a == saved
                    determinant = matrix_determinant(a, mod)
                    diagonal = [[determinant * (i == j) for j in range(n)] for i in range(n)]
                    assert matrix_multiply(a, result, mod) == diagonal
                    assert matrix_multiply(result, a, mod) == diagonal


def test_adjugate_boundaries():
    assert adjugate([]) == []
    assert adjugate([[0]]) == [[1]]
    assert adjugate([[-7]], 2) == [[1]]
    for a in ([[1, 2]], [[1], [2]], [[1, 2], [3]]):
        with pytest.raises(ValueError):
            adjugate(a)
    with pytest.raises(ValueError):
        adjugate([[1]], 1)
    a = [[10**70 + 3, -2], [7, -(10**100)]]
    assert adjugate(a, 101) == oracle(a, 101)
    assert adjugate(a, 2**61 - 1) == oracle(a, 2**61 - 1)


def test_adjugate_catalog_and_article():
    root = Path(__file__).resolve().parents[2]
    data = json.loads((root / "library-catalog.json").read_text())
    module = next(m for m in data["modules"] if m["modulePath"] == "library_codex.linear_algebra.Adjugate")
    assert "余因子行列" in module["searchTerms"]
    assert module["bundledDependencies"] == []
    assert "O(N³ + N log mod)" in module["complexity"]
    function = module["functions"][0]
    assert function["name"] == "adjugate"
    assert "j行目とi列目" in function["returns"]
    namespace = {}
    exec(module["standaloneCode"], namespace)
    assert namespace["adjugate"]([[1, 2], [2, 4]], 7) == [[4, 5], [5, 1]]
    for example in re.findall(r"```python\n(.*?)\n```", module["article"]["markdown"], re.S):
        exec(example, {})
