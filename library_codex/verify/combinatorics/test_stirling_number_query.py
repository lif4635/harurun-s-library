from array import array
from math import comb, factorial
from pathlib import Path
import random
import subprocess
import sys

import pytest

from library_codex.combinatorics.StirlingNumberQuery import StirlingNumberQuery
from library_codex.tools.build_library_catalog import build_standalone_code


@pytest.mark.parametrize("p", [2, 3, 5, 7, 11, 17, 31])
@pytest.mark.parametrize("kind", [1, 2])
def test_stirling_number_query_against_dp(p, kind):
    solver = StirlingNumberQuery(p)
    query = solver.first_kind if kind == 1 else solver.second_kind
    prev = [1]
    for n in range(301):
        if n:
            row = [0] * (n + 1)
            row[n] = 1
            for k in range(1, n):
                coefficient = -(n - 1) if kind == 1 else k
                row[k] = (prev[k - 1] + coefficient * prev[k]) % p
            prev = row
        assert [query(n, k) for k in range(n + 1)] == prev
        assert query(n, -1) == query(n, n + 1) == 0


@pytest.mark.parametrize("kind", [1, 2])
def test_stirling_number_query_large_recurrence_and_boundaries(kind):
    rng = random.Random(51431)
    for p in (2, 3, 7, 97):
        solver = StirlingNumberQuery(p)
        query = solver.first_kind if kind == 1 else solver.second_kind
        for _ in range(600):
            n = rng.randrange(2, 10**18 + 1)
            k = rng.choice((1, n, n - 1, rng.randrange(1, n + 1)))
            coefficient = -(n - 1) if kind == 1 else k
            assert query(n, k) == (query(n - 1, k - 1) + coefficient * query(n - 1, k)) % p
            assert query(n, n) == 1
            assert query(n, 0) == 0
            assert query(n, n - 1) == (1 if kind == 2 else -1) * comb(n, 2) % p
            assert query(n, 1) == (0 if kind == 1 else 1)
        assert query(0, 0) == 1


def test_stirling_number_query_second_kind_inclusion_exclusion():
    for p in (5, 11, 101):
        query = StirlingNumberQuery(p).second_kind
        for n in (p, p * p, 10**18 - 1, 10**18):
            for k in range(1, min(p, 30)):
                expected = sum((-1)**(k - j) * comb(k, j) * pow(j, n, p) for j in range(k + 1))
                assert query(n, k) == expected * pow(factorial(k), -1, p) % p


def test_stirling_number_query_storage_and_validation():
    solver = StirlingNumberQuery(101)
    assert solver.first is solver.second is None
    assert solver.first_kind(5, 2) == -50 % 101
    assert solver.second is None
    assert len(solver.first) == 101
    assert all(isinstance(row, array) and row.typecode == "H" for row in solver.first)
    assert sum(len(row) for row in solver.first) == 101 * 102 // 2
    first = solver.first
    assert solver.second_kind(5, 2) == 15
    second = solver.second
    assert solver.FirstKind(5, 2) == -50 % 101
    assert solver.SecondKind(5, 2) == 15
    assert solver.first is first and solver.second is second
    assert repr(solver) == "StirlingNumberQuery(prime=101)"
    assert solver.first is first and solver.second is second
    only_second = StirlingNumberQuery(7)
    assert only_second.second_kind(5, 2) == 1
    assert only_second.first is None
    for p in (-1, 0, 1, 4, 9, 25, 65536, 65537):
        with pytest.raises(ValueError):
            StirlingNumberQuery(p)
    assert solver.first_kind(-1, 0) == solver.second_kind(-1, 0) == 0


def test_stirling_number_query_standalone(tmp_path):
    root = Path(__file__).resolve().parents[2]
    source, dependencies = build_standalone_code(root / "combinatorics/StirlingNumberQuery.py", root)
    assert dependencies == []
    script = tmp_path / "main.py"
    script.write_text(source + '\nquery = StirlingNumberQuery(7)\nassert query.second_kind(5, 2) == 1\nassert query.first_kind(5, 2) == 6\n', encoding="utf-8")
    subprocess.run([sys.executable, "-I", str(script)], cwd=tmp_path, check=True, timeout=30)
