"""DAGが表す半順序の最大反鎖を求める。"""

from library_codex.graph_matching.BipartiteMatching import BipartiteMatching


def _to_vertex(edge):
    return edge if isinstance(edge, int) else edge[0]


def maximum_antichain(graph):
    """互いに到達不能な頂点を最大個数選んで返す。"""
    n = len(graph)
    adjacency = [[] for _ in range(n)]
    indegree = [0] * n
    for vertex, row in enumerate(graph):
        target = adjacency[vertex]
        for edge in row:
            to = _to_vertex(edge)
            if not 0 <= to < n:
                raise IndexError("an edge endpoint is outside the graph")
            target.append(to)
            indegree[to] += 1

    order = [v for v in range(n) if indegree[v] == 0]
    head = 0
    while head < len(order):
        vertex = order[head]
        head += 1
        for to in adjacency[vertex]:
            indegree[to] -= 1
            if indegree[to] == 0:
                order.append(to)
    if len(order) != n:
        raise ValueError("maximum_antichain requires a DAG")

    reachable = [0] * n
    for vertex in reversed(order):
        bits = 0
        for to in adjacency[vertex]:
            bits |= reachable[to] | (1 << to)
        reachable[vertex] = bits

    matcher = BipartiteMatching(n, n)
    for vertex, bits in enumerate(reachable):
        while bits:
            least = bits & -bits
            matcher.add_edge(vertex, least.bit_length() - 1)
            bits ^= least
    left_cover, right_cover = matcher.minimum_vertex_cover()
    excluded = bytearray(n)
    for vertex in left_cover:
        excluded[vertex] = 1
    for vertex in right_cover:
        excluded[vertex] = 1
    return [vertex for vertex in range(n) if not excluded[vertex]]
