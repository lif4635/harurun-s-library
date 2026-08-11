"""単純無向グラフがcactusか判定し、辺をcycleへ分解する。"""


def decompose(vertex_count, edges):
    """各辺が高々1個の単純cycleに属するならcycle列と所属表を返す。"""
    if vertex_count < 0:
        raise ValueError("vertex_count must be nonnegative")
    edges = list(edges)
    graph = [[] for _ in range(vertex_count)]
    used_pairs = set()
    for edge_id, (first, second) in enumerate(edges):
        if not 0 <= first < vertex_count or not 0 <= second < vertex_count:
            raise IndexError("an edge endpoint is outside the graph")
        if first == second:
            return None
        pair = (first, second) if first < second else (second, first)
        if pair in used_pairs:
            return None
        used_pairs.add(pair)
        graph[first].append((second, edge_id))
        graph[second].append((first, edge_id))

    parent = [-1] * vertex_count
    parent_edge = [-1] * vertex_count
    depth = [0] * vertex_count
    state = bytearray(vertex_count)
    back_edges = []
    for root in range(vertex_count):
        if state[root]:
            continue
        state[root] = 1
        stack = [(root, 0)]
        while stack:
            vertex, index = stack[-1]
            if index == len(graph[vertex]):
                state[vertex] = 2
                stack.pop()
                continue
            to, edge_id = graph[vertex][index]
            stack[-1] = (vertex, index + 1)
            if edge_id == parent_edge[vertex]:
                continue
            if state[to] == 0:
                parent[to] = vertex
                parent_edge[to] = edge_id
                depth[to] = depth[vertex] + 1
                state[to] = 1
                stack.append((to, 0))
            elif state[to] == 1 and depth[to] < depth[vertex]:
                back_edges.append((vertex, to, edge_id))

    edge_cycle = [-1] * len(edges)
    cycles = []
    for descendant, ancestor, closing_edge in back_edges:
        path = []
        vertex = descendant
        while depth[vertex] > depth[ancestor]:
            edge_id = parent_edge[vertex]
            if edge_cycle[edge_id] != -1:
                return None
            path.append(edge_id)
            vertex = parent[vertex]
        if vertex != ancestor or edge_cycle[closing_edge] != -1:
            return None
        cycle_id = len(cycles)
        cycle = list(reversed(path))
        cycle.append(closing_edge)
        for edge_id in cycle:
            edge_cycle[edge_id] = cycle_id
        cycles.append(cycle)
    return cycles, edge_cycle


def is_cactus(vertex_count, edges):
    """単純無向グラフの各辺が高々1個の単純cycleに属するか返す。"""
    return decompose(vertex_count, edges) is not None
