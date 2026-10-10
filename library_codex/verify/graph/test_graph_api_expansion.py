import random

from library_codex.graph.TournamentPath import tournament_hamiltonian_path
from library_codex.tree.TreeDiameter import tree_metric_center


def test_tournament_hamiltonian_path_random():
    random.seed(20260825)
    for n in range(50):
        graph = [[] for _ in range(n)]
        for first in range(n):
            for second in range(first + 1, n):
                if random.randrange(2):
                    graph[first].append(second)
                else:
                    graph[second].append(first)
        path = tournament_hamiltonian_path(graph)
        assert sorted(path) == list(range(n))
        assert all(path[i + 1] in graph[path[i]] for i in range(n - 1))


def test_weighted_tree_metric_center_vertex_and_edge():
    tree = [[(1, 2)], [(0, 2), (2, 4)], [(1, 4)]]
    assert tree_metric_center(tree) == (3, (1, 2, 1))
    unweighted = [[1], [0, 2], [1, 3], [2]]
    assert tree_metric_center(unweighted) == (1.5, (1, 2, 0.5))
