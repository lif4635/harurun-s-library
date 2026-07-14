import itertools
import random
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[3]))

from library_codex.graph.MinCostFlow import MinCostFlowGraph


def brute(n, edges, source, sink):
    best = {}
    ranges = [range(cap + 1) for _, _, cap, _ in edges]
    for flows in itertools.product(*ranges):
        balance = [0] * n
        cost = 0
        for flow, (u, v, _, c) in zip(flows, edges):
            balance[u] -= flow
            balance[v] += flow
            cost += flow * c
        if any(balance[v] for v in range(n) if v not in (source, sink)):
            continue
        flow = -balance[source]
        if flow < 0 or balance[sink] != flow:
            continue
        if flow not in best or cost < best[flow]:
            best[flow] = cost
    return best


def expand_slope(points):
    result = {0: 0}
    for (f0, c0), (f1, c1) in zip(points, points[1:]):
        unit = (c1 - c0) // (f1 - f0)
        for f in range(f0 + 1, f1 + 1):
            result[f] = c0 + (f - f0) * unit
    return result


def test_random_against_enumeration():
    for n in range(2, 6):
        for _ in range(3000):
            source = 0
            sink = n - 1
            edges = []
            for _ in range(random.randrange(8)):
                u = random.randrange(n)
                v = random.randrange(n)
                cap = random.randrange(3)
                cost = random.randrange(10)
                edges.append((u, v, cap, cost))
            want = brute(n, edges, source, sink)
            graph = MinCostFlowGraph(n)
            for edge in edges:
                graph.add_edge(*edge)
            points = graph.slope(source, sink)
            got = expand_slope(points)
            max_flow = max(want)
            assert points[-1][0] == max_flow
            assert got == {f: want[f] for f in range(max_flow + 1)}
            for _, _, cap, flow, _ in graph.edges():
                assert 0 <= flow <= cap


def test_limit_and_repeated_flow():
    edges = [(0, 1, 3, 2), (0, 2, 2, 1), (2, 1, 2, 0), (1, 3, 5, 4)]
    graph = MinCostFlowGraph(4)
    for edge in edges:
        graph.add_edge(*edge)
    assert graph.flow(0, 3, 2) == (2, 10)
    assert graph.flow(0, 3, 2) == (2, 12)
    assert graph.flow(0, 3) == (1, 6)
    assert graph.flow(0, 3) == (0, 0)


def test_long_without_recursion():
    n = 100000
    graph = MinCostFlowGraph(n)
    for i in range(n - 1):
        graph.add_edge(i, i + 1, 3, i & 7)
    want = 3 * sum(i & 7 for i in range(n - 1))
    assert graph.flow(0, n - 1) == (3, want)


if __name__ == "__main__":
    random.seed(0)
    test_random_against_enumeration()
    test_limit_and_repeated_flow()
    test_long_without_recursion()
