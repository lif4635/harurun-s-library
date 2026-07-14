import heapq
import itertools
import random
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from graph.GraphOptimization import (  # noqa: E402
    dial_dijkstra,
    held_karp_cycle,
    held_karp_path,
    hungarian,
    hungarian_max,
    minimum_cost_arborescence,
    minimum_steiner_tree,
    steiner_tree_dp,
)


def test_hungarian_rectangular_against_permutations():
    rng = random.Random(10)
    for rows in range(6):
        for columns in range(max(1, rows), 7):
            for _ in range(80):
                cost = [[rng.randrange(-20, 21) for _ in range(columns)]
                        for _ in range(rows)]
                expected_min = min(
                    (sum(cost[i][p[i]] for i in range(rows)), p)
                    for p in itertools.permutations(range(columns), rows)
                ) if rows else (0, ())
                expected_max = max(
                    (sum(cost[i][p[i]] for i in range(rows)), p)
                    for p in itertools.permutations(range(columns), rows)
                ) if rows else (0, ())
                value, assignment = hungarian(cost)
                assert value == expected_min[0]
                assert len(set(assignment)) == rows
                assert value == sum(cost[i][assignment[i]] for i in range(rows))
                value, assignment = hungarian_max(cost)
                assert value == expected_max[0]
                assert len(set(assignment)) == rows
                assert value == sum(cost[i][assignment[i]] for i in range(rows))


def _connected_terminals(n, edges, selected, terminals):
    if not terminals:
        return True
    graph = [[] for _ in range(n)]
    for edge_id in selected:
        u, v, _ = edges[edge_id]
        graph[u].append(v)
        graph[v].append(u)
    seen = {terminals[0]}
    stack = [terminals[0]]
    while stack:
        v = stack.pop()
        for to in graph[v]:
            if to not in seen:
                seen.add(to)
                stack.append(to)
    return all(v in seen for v in terminals)


def test_minimum_steiner_tree_against_edge_subsets():
    rng = random.Random(11)
    for n in range(2, 8):
        pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
        for _ in range(100):
            rng.shuffle(pairs)
            chosen_pairs = pairs[:rng.randrange(min(len(pairs), 8) + 1)]
            edges = [(u, v, rng.randrange(7)) for u, v in chosen_pairs]
            terminals = rng.sample(range(n), rng.randrange(1, min(4, n) + 1))
            expected = float("inf")
            for mask in range(1 << len(edges)):
                selected = [i for i in range(len(edges)) if mask >> i & 1]
                if _connected_terminals(n, edges, selected, terminals):
                    expected = min(expected, sum(edges[i][2] for i in selected))
            value, selected = minimum_steiner_tree(n, edges, terminals)
            assert value == expected
            if value < float("inf"):
                assert _connected_terminals(n, edges, selected, terminals)
                assert sum(edges[i][2] for i in selected) == value
            table = steiner_tree_dp(n, edges, terminals)
            assert min(table[-1]) == expected


def test_held_karp_path_and_cycle_against_permutations():
    rng = random.Random(12)
    for n in range(1, 9):
        for _ in range(30):
            distance = [[0 if u == v else rng.randrange(-5, 15)
                         for v in range(n)] for u in range(n)]
            for start in (None, rng.randrange(n)):
                goals = (None, rng.randrange(n))
                for goal in goals:
                    if start is not None and goal == start and n > 1:
                        continue
                    orders = itertools.permutations(range(n))
                    expected = min(
                        sum(distance[p[i]][p[i + 1]] for i in range(n - 1))
                        for p in orders
                        if (start is None or p[0] == start)
                        and (goal is None or p[-1] == goal)
                    )
                    value, order = held_karp_path(
                        distance, start, goal, restore=True
                    )
                    assert value == expected
                    assert sorted(order) == list(range(n))
                    assert value == sum(distance[order[i]][order[i + 1]]
                                        for i in range(n - 1))
            if n > 1:
                start = rng.randrange(n)
                expected = min(
                    sum(distance[p[i]][p[i + 1]] for i in range(n - 1))
                    + distance[p[-1]][start]
                    for p in itertools.permutations(range(n)) if p[0] == start
                )
                value, order = held_karp_cycle(distance, start, restore=True)
                assert value == expected
                assert order[0] == order[-1] == start
                assert sorted(order[:-1]) == list(range(n))


def _heap_dijkstra(graph, starts):
    n = len(graph)
    distance = [float("inf")] * n
    heap = []
    for start in starts:
        distance[start] = 0
        heapq.heappush(heap, (0, start))
    while heap:
        dist, v = heapq.heappop(heap)
        if distance[v] != dist:
            continue
        for to, weight in graph[v]:
            nxt = dist + weight
            if nxt < distance[to]:
                distance[to] = nxt
                heapq.heappush(heap, (nxt, to))
    return distance


def test_dial_dijkstra_random_and_zero_edges():
    rng = random.Random(13)
    for n in range(1, 60):
        for _ in range(20):
            maximum = rng.randrange(10)
            graph = [[] for _ in range(n)]
            for u in range(n):
                for v in range(n):
                    if rng.randrange(15) == 0:
                        graph[u].append((v, rng.randrange(maximum + 1)))
            starts = rng.sample(range(n), rng.randrange(1, min(5, n) + 1))
            expected = _heap_dijkstra(graph, starts)
            distance, parent = dial_dijkstra(
                graph, starts, maximum, restore=True
            )
            assert distance == expected
            for v in range(n):
                if parent[v] != -1:
                    assert any(to == v and distance[parent[v]] + weight == distance[v]
                               for to, weight in graph[parent[v]])


def _is_arborescence(n, root, edges, selected):
    if len(selected) != n - 1:
        return False
    graph = [[] for _ in range(n)]
    indegree = [0] * n
    for edge_id in selected:
        u, v, _ = edges[edge_id]
        graph[u].append(v)
        indegree[v] += 1
    if indegree[root] or any(indegree[v] != 1 for v in range(n) if v != root):
        return False
    seen = {root}
    stack = [root]
    while stack:
        v = stack.pop()
        for to in graph[v]:
            if to not in seen:
                seen.add(to)
                stack.append(to)
    return len(seen) == n


def test_minimum_cost_arborescence_against_edge_subsets():
    rng = random.Random(14)
    for n in range(1, 7):
        for _ in range(500):
            root = rng.randrange(n)
            possible = [(u, v) for u in range(n) for v in range(n) if u != v]
            rng.shuffle(possible)
            edge_count = rng.randrange(min(10, len(possible)) + 1)
            edges = [(u, v, rng.randrange(-8, 12))
                     for u, v in possible[:edge_count]]
            # Occasionally add a parallel edge.
            if edges and rng.randrange(3) == 0:
                u, v, _ = rng.choice(edges)
                edges.append((u, v, rng.randrange(-8, 12)))
            expected = float("inf")
            for selected in itertools.combinations(range(len(edges)), n - 1):
                if _is_arborescence(n, root, edges, selected):
                    expected = min(expected,
                                   sum(edges[i][2] for i in selected))
            result = minimum_cost_arborescence(n, root, edges)
            if expected == float("inf"):
                assert result is None
            else:
                value, selected = result
                assert value == expected
                assert _is_arborescence(n, root, edges, selected)
