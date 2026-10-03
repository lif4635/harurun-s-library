import random

from library_codex.graph_connectivity.StronglyConnectedComponents import scc_ids


def test_scc_ids_against_transitive_closure():
    rng = random.Random(927)
    for n in range(20):
        for _ in range(40):
            graph = [[j for j in range(n) if rng.randrange(5) == 0] for i in range(n)]
            reach = [[i == j or j in graph[i] for j in range(n)] for i in range(n)]
            for k in range(n):
                for i in range(n):
                    for j in range(n):
                        reach[i][j] |= reach[i][k] and reach[k][j]
            count, ids = scc_ids(graph)
            assert set(ids) == set(range(count))
            for i in range(n):
                for j in range(n):
                    assert (ids[i] == ids[j]) == (reach[i][j] and reach[j][i])
                for j in graph[i]:
                    assert ids[i] <= ids[j]
            weighted = [[(j, -5) for j in row] for row in graph]
            assert scc_ids(weighted) == (count, ids)


def test_scc_ids_long_chain_and_cycle():
    n = 100000
    graph = [[i + 1] for i in range(n - 1)] + [[]]
    count, ids = scc_ids(graph)
    assert count == n
    assert ids == list(range(n))
    graph[-1].append(0)
    assert scc_ids(graph) == (1, [0] * n)
