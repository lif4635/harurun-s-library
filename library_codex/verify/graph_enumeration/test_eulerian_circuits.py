from itertools import permutations
from math import factorial
import random
from pathlib import Path
import subprocess
import sys

import pytest

from library_codex.graph_enumeration.EulerianCircuits import count_eulerian_circuits
from library_codex.tools.build_library_catalog import build_standalone_code


def brute(edges):
    if not edges:
        return 0
    answer = 0
    for rest in permutations(range(1, len(edges))):
        order = (0,) + rest
        if all(edges[order[i]][1] == edges[order[(i + 1) % len(edges)]][0] for i in range(len(edges))):
            answer += 1
    return answer


def test_eulerian_circuits_against_edge_permutations():
    rng = random.Random(71509)
    for _ in range(250):
        n = rng.randrange(1, 6)
        edges = [(rng.randrange(n), rng.randrange(n)) for _ in range(rng.randrange(1, 9))]
        expected = brute(edges)
        for mod in (2, 3, 7, 998244353):
            assert count_eulerian_circuits(n, edges, mod) == expected % mod
    for _ in range(80):
        n = rng.randrange(1, 6)
        walk = [rng.randrange(n) for _ in range(rng.randrange(1, 9))]
        edges = list(zip(walk, walk[1:] + walk[:1]))
        assert count_eulerian_circuits(n + 3, iter(edges)) == brute(edges)


def test_eulerian_circuits_isolation_loops_and_disconnection():
    assert count_eulerian_circuits(0, []) == 0
    assert count_eulerian_circuits(20, []) == 0
    for n in range(1, 30):
        assert count_eulerian_circuits(20, [(7, 7)] * n) == factorial(n - 1) % 998244353
    assert count_eulerian_circuits(4, [(0, 1), (1, 0), (2, 3), (3, 2)]) == 0
    assert count_eulerian_circuits(2, [(0, 1), (0, 1)]) == 0
    assert count_eulerian_circuits(2, [(0, 1)] * 4 + [(1, 0)] * 4) == 144


def test_eulerian_circuits_invalid_input():
    with pytest.raises(ValueError):
        count_eulerian_circuits(-1, [])
    with pytest.raises(ValueError):
        count_eulerian_circuits(1, [], 1)
    for edge in ((-1, 0), (0, 2)):
        with pytest.raises(IndexError):
            count_eulerian_circuits(2, [edge])


def test_eulerian_circuits_standalone(tmp_path):
    root = Path(__file__).resolve().parents[2]
    source, dependencies = build_standalone_code(root / "graph_enumeration/EulerianCircuits.py", root)
    assert dependencies == []
    assert "def inverse_matrix(" not in source
    assert "from library_codex" not in source
    script = tmp_path / "main.py"
    script.write_text(source + '\nassert count_eulerian_circuits(2, [(0, 1)] * 4 + [(1, 0)] * 4) == 144\n', encoding="utf-8")
    subprocess.run([sys.executable, "-I", str(script)], cwd=tmp_path, check=True, timeout=30)
