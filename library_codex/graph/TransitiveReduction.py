"""DAGの到達関係を変えず、推移的に不要な辺を取り除く。"""


def _to_vertex(edge):
    return edge if isinstance(edge, int) else edge[0]


def transitive_reduction(graph):
    """graphと同じ到達関係をもつ、辺数最小のDAG隣接listを返す。"""
    n = len(graph)
    adjacency = [[] for _ in range(n)]
    indegree = [0] * n
    for vertex, row in enumerate(graph):
        seen = set()
        for edge in row:
            to = _to_vertex(edge)
            if not 0 <= to < n:
                raise IndexError("an edge endpoint is outside the graph")
            if to not in seen:
                seen.add(to)
                adjacency[vertex].append(to)
                indegree[to] += 1

    order = [vertex for vertex in range(n) if indegree[vertex] == 0]
    head = 0
    while head < len(order):
        vertex = order[head]
        head += 1
        for to in adjacency[vertex]:
            indegree[to] -= 1
            if indegree[to] == 0:
                order.append(to)
    if len(order) != n:
        raise ValueError("transitive_reduction requires a DAG")

    position = [0] * n
    for index, vertex in enumerate(order):
        position[vertex] = index
    reachable = [0] * n
    result = [[] for _ in range(n)]
    for vertex in reversed(order):
        covered = 0
        kept = result[vertex]
        for to in sorted(adjacency[vertex], key=position.__getitem__):
            bit = 1 << to
            if covered & bit:
                continue
            kept.append(to)
            covered |= bit | reachable[to]
        reachable[vertex] = covered
    return result
