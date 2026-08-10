import random

from library_codex.graph_connectivity.DominatorTree import dominator_tree


def _brute_idom(graph, root):
    size = len(graph)
    reverse = [[] for _ in graph]
    reachable = [False] * size
    reachable[root] = True
    stack = [root]
    while stack:
        vertex = stack.pop()
        for target in graph[vertex]:
            reverse[target].append(vertex)
            if not reachable[target]:
                reachable[target] = True
                stack.append(target)

    vertices = {vertex for vertex in range(size) if reachable[vertex]}
    dominators = [set() for _ in graph]
    dominators[root] = {root}
    for vertex in vertices:
        if vertex != root:
            dominators[vertex] = set(vertices)
    changed = True
    while changed:
        changed = False
        for vertex in vertices:
            if vertex == root:
                continue
            predecessors = [source for source in reverse[vertex] if reachable[source]]
            common = set(vertices)
            for source in predecessors:
                common &= dominators[source]
            current = common | {vertex}
            if current != dominators[vertex]:
                dominators[vertex] = current
                changed = True

    answer = [-1] * size
    answer[root] = root
    for vertex in vertices:
        if vertex == root:
            continue
        strict = dominators[vertex] - {vertex}
        answer[vertex] = max(strict, key=lambda node: len(dominators[node]))
    return answer


def test_dominator_tree_against_fixed_point_definition():
    rng = random.Random(781239)
    for size in range(1, 10):
        for _ in range(1000):
            graph = [[] for _ in range(size)]
            for source in range(size):
                for target in range(size):
                    if rng.randrange(5) == 0:
                        graph[source].append(target)
            root = rng.randrange(size)
            expected = _brute_idom(graph, root)
            assert dominator_tree(graph, root) == expected
            weighted = [[(target, 1) for target in row] for row in graph]
            assert dominator_tree(weighted, root) == expected


def test_dominator_tree_root_and_unreachable_vertices():
    graph = [[1, 2], [3], [3], [], [3]]
    assert dominator_tree(graph, 0) == [0, 0, 0, 0, -1]
