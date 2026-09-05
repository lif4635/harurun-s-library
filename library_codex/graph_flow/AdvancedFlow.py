from library_codex.graph_flow.PushRelabel import PushRelabel


def gomory_hu_tree(n, edges, flow_class=PushRelabel):
    """Return an undirected Gomory--Hu cut tree as ``(u, v, cut)`` edges.

    Parallel edges and zero-capacity edges are accepted. ``edges`` is consumed
    once and materialized because the max-flow graph is rebuilt ``n - 1`` times.
    """
    if n < 0:
        raise ValueError("number of vertices must be nonnegative")
    edges = list(edges)
    for source, target, capacity in edges:
        if not (0 <= source < n and 0 <= target < n):
            raise IndexError("vertex out of range")
        if capacity < 0:
            raise ValueError("capacity must be nonnegative")
    if n <= 1:
        return []

    parent = [0] * n
    value = [0] * n
    for source in range(1, n):
        sink = parent[source]
        flow = flow_class(n)
        for left, right, capacity in edges:
            if left != right and capacity:
                flow.add_edge(left, right, capacity)
                flow.add_edge(right, left, capacity)
        cut_value = flow.flow(source, sink)
        side = flow.min_cut(source)

        for vertex in range(source + 1, n):
            if parent[vertex] == sink and side[vertex]:
                parent[vertex] = source
        sink_parent = parent[sink]
        if side[sink_parent]:
            parent[source] = sink_parent
            parent[sink] = source
            value[source] = value[sink]
            value[sink] = cut_value
        else:
            value[source] = cut_value

    return [(vertex, parent[vertex], value[vertex]) for vertex in range(1, n)]


def stoer_wagner_min_cut(n, edges):
    """Return ``(cut_value, one_side)`` for an undirected weighted graph.

    This dense ``O(V^3)`` implementation is useful when running ``V - 1``
    max-flow computations would be more expensive. The graph may be
    disconnected, in which case the returned minimum value is zero.
    """
    if n < 0:
        raise ValueError("number of vertices must be nonnegative")
    if n == 0:
        return 0, []
    matrix = [[0] * n for _ in range(n)]
    for source, target, weight in edges:
        if not (0 <= source < n and 0 <= target < n):
            raise IndexError("vertex out of range")
        if weight < 0:
            raise ValueError("weight must be nonnegative")
        if source != target:
            matrix[source][target] += weight
            matrix[target][source] += weight
    if n == 1:
        return 0, [0]

    vertices = list(range(n))
    groups = [[vertex] for vertex in range(n)]
    best_value = None
    best_side = []

    while len(vertices) > 1:
        weights = [0] * n
        used = bytearray(n)
        previous = -1
        for step in range(len(vertices)):
            selected = -1
            selected_weight = -1
            for vertex in vertices:
                if not used[vertex] and weights[vertex] > selected_weight:
                    selected = vertex
                    selected_weight = weights[vertex]

            if step + 1 == len(vertices):
                if best_value is None or selected_weight < best_value:
                    best_value = selected_weight
                    best_side = groups[selected][:]
                for vertex in vertices:
                    if vertex != selected and vertex != previous:
                        merged = matrix[previous][vertex] + matrix[selected][vertex]
                        matrix[previous][vertex] = merged
                        matrix[vertex][previous] = merged
                groups[previous].extend(groups[selected])
                vertices.remove(selected)
                break

            used[selected] = 1
            previous = selected
            selected_row = matrix[selected]
            for vertex in vertices:
                if not used[vertex]:
                    weights[vertex] += selected_row[vertex]

    return best_value, best_side
