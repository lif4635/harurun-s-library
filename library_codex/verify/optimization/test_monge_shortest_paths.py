import random
import json
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

import pytest

from library_codex.optimization.MongeShortestPaths import (
    enumerate_monge_d_edge_shortest_paths,
    monge_d_edge_shortest_path,
    monge_shortest_paths,
)


def exact_distances(n, cost):
    previous = [0] + [float("inf")] * n
    answer = [previous[n]]
    for _ in range(n):
        current = [float("inf")] * (n + 1)
        for j in range(1, n + 1):
            current[j] = min(previous[i] + cost(i, j) for i in range(j))
        previous = current
        answer.append(current[n])
    return answer


def monge_matrix(n, rng):
    rows = [rng.randrange(-100, 101) for _ in range(n + 1)]
    cols = [rng.randrange(-100, 101) for _ in range(n + 1)]
    prefix = [[0] * (n + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for j in range(1, n + 1):
            prefix[i][j] = (prefix[i - 1][j] + prefix[i][j - 1]
                            - prefix[i - 1][j - 1] + rng.randrange(6))
    return [[rows[i] + cols[j] - prefix[i][j] for j in range(n + 1)]
            for i in range(n + 1)]


def test_random_monge_matrices_against_cubic_dp():
    rng = random.Random(6207)
    for n in range(1, 25):
        for _ in range(12):
            matrix = monge_matrix(n, rng)

            def cost(i, j):
                assert 0 <= i < j <= n
                return matrix[i][j]

            expected = exact_distances(n, cost)
            actual = enumerate_monge_d_edge_shortest_paths(n, cost, float("inf"))
            assert actual == expected
            distance = [0]
            for j in range(1, n + 1):
                distance.append(min(distance[i] + cost(i, j) for i in range(j)))
            assert monge_shortest_paths(n, cost) == distance
            for k in range(n + 1):
                assert monge_d_edge_shortest_path(n, k, cost, float("inf")) == expected[k]


@pytest.mark.parametrize("bias", [-1000, -1, 0, 1, 1000])
def test_tied_optima_and_both_penalty_directions(bias):
    n = 128
    for k in (3, 7, 31, 64, 127):
        assert monge_d_edge_shortest_path(n, k, lambda i, j: bias) == bias * k
        q, r = divmod(n, k)
        expected = (k - r) * q * q + r * (q + 1) ** 2 + bias * k
        assert monge_d_edge_shortest_path(n, k, lambda i, j: (j - i) ** 2 + bias) == expected


def test_boundaries_and_shortcuts():
    def unused(i, j):
        raise AssertionError("cost must not be called")

    assert monge_d_edge_shortest_path(0, 0, unused) == 0
    assert monge_d_edge_shortest_path(10, 0, unused, None) is None
    assert monge_d_edge_shortest_path(10, 11, unused, None) is None
    assert monge_d_edge_shortest_path(10, -1, unused, None) is None
    with pytest.raises(ValueError):
        monge_d_edge_shortest_path(-1, 0, unused)
    assert enumerate_monge_d_edge_shortest_paths(0, unused) == [0]
    assert monge_d_edge_shortest_path(1, 1, lambda i, j: -10 ** 150) == -10 ** 150


def test_large_integers_and_noninteger_weights():
    n = 15
    for scale in (10 ** 120, 0.25, Fraction(1, 3)):
        cost = lambda i, j: scale * ((j - i) ** 2 - 5)
        expected = exact_distances(n, cost)
        for k in range(1, n + 1):
            assert monge_d_edge_shortest_path(n, k, cost, float("inf"), integer=isinstance(scale, int)) == expected[k]
            assert monge_d_edge_shortest_path(n, k, cost, integer=isinstance(scale, int)) == expected[k]
        assert enumerate_monge_d_edge_shortest_paths(n, cost)[1:] == expected[1:]
    matrix = monge_matrix(18, random.Random(17))
    cost = lambda i, j: matrix[i][j] + (0.5 if j == 7 else 0)
    expected = exact_distances(18, cost)
    for k in range(1, 19):
        assert monge_d_edge_shortest_path(18, k, cost, float("inf"), integer=False) == expected[k]
    with pytest.raises(TypeError, match="integer=False"):
        monge_d_edge_shortest_path(15, 7, lambda i, j: 0.5 * (j - i) ** 2)


def test_cost_call_growth_is_not_linear_in_k():
    n = 4096
    for k in (n // 4, n // 2):
        calls = 0

        def cost(i, j):
            nonlocal calls
            calls += 1
            return (j - i) ** 2

        q, r = divmod(n, k)
        expected = (k - r) * q * q + r * (q + 1) ** 2
        assert monge_d_edge_shortest_path(n, k, cost) == expected
        assert calls < 150 * n * n.bit_length()


def test_catalog_and_standalone(tmp_path):
    catalog = json.loads((Path(__file__).resolve().parents[2] / "library-catalog.json").read_text())
    module = next(item for item in catalog["modules"]
                  if item["modulePath"] == "library_codex.optimization.MongeShortestPaths")
    assert "k辺最短路" in module["searchTerms"]
    function = next(item for item in module["functions"] if item["name"] == "monge_d_edge_shortest_path")
    assert "integer=True" in function["signature"]
    assert "log(2+NW)" in function["complexity"]
    assert "ちょうど" in function["description"]
    script = tmp_path / "standalone.py"
    script.write_text(module["standaloneCode"] + "\nassert monge_d_edge_shortest_path(1000, 500, lambda i, j: (j-i)**2) == 2000\n")
    subprocess.run([sys.executable, "-I", str(script)], cwd=tmp_path, check=True, timeout=20)
