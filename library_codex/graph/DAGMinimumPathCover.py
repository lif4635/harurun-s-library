"""DAGを覆う頂点素なpathの最小本数を求める。"""

from graph.BipartiteMatching import BipartiteMatching

def dag_minimum_path_cover(graph):
    """Return a minimum vertex-disjoint path cover of a DAG.

    The caller is responsible for the DAG precondition.  The result is a list
    of vertex lists and has size N minus the maximum bipartite matching size.
    """
    n = len(graph)
    matching = BipartiteMatching(n, n)
    for source, row in enumerate(graph):
        for target in row:
            matching.add_edge(source, target)
    matching.solve()
    successor = matching.match_left
    predecessor = matching.match_right
    paths = []
    used = [False] * n
    for start in range(n):
        if predecessor[start] != -1:
            continue
        path = []
        vertex = start
        while vertex != -1 and not used[vertex]:
            used[vertex] = True
            path.append(vertex)
            vertex = successor[vertex]
        paths.append(path)
    for start in range(n):
        if not used[start]:
            path = []
            vertex = start
            while vertex != -1 and not used[vertex]:
                used[vertex] = True
                path.append(vertex)
                vertex = successor[vertex]
            paths.append(path)
    return paths

