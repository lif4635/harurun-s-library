"""指定rootから全頂点へ到達する有向全域木の最小費用を求める。"""

def minimum_cost_arborescence(n, root, edges):
    """Return a minimum directed spanning arborescence rooted at ``root``.

    Edges are ``(source, target, cost)`` and may have negative costs or be
    parallel.  The result is ``(cost, original_edge_ids)``; ``None`` means some
    vertex is unreachable from the root.  This iterative Chu--Liu/Edmonds
    implementation runs in O(VE).
    """
    if n == 0:
        return 0, []
    if not 0 <= root < n:
        raise IndexError("root out of range")
    # Each current edge stores source, target, adjusted cost, original edge id.
    current_edges = [(u, v, cost, i) for i, (u, v, cost) in enumerate(edges)]
    current_n = n
    current_root = root
    # (old edges, old root, chosen incoming edge per old vertex,
    #  mapping from each next-level edge to its old-level edge)
    levels = []

    while True:
        incoming_cost = [float("inf")] * current_n
        incoming_edge = [-1] * current_n
        incoming_cost[current_root] = 0
        for edge_id, (u, v, cost, _) in enumerate(current_edges):
            if u != v and v != current_root and cost < incoming_cost[v]:
                incoming_cost[v] = cost
                incoming_edge[v] = edge_id
        if any(incoming_edge[v] == -1
               for v in range(current_n) if v != current_root):
            return None

        parent = [current_root] * current_n
        for v in range(current_n):
            if v != current_root:
                parent[v] = current_edges[incoming_edge[v]][0]
        component = [-1] * current_n
        visited = [-1] * current_n
        cycle_count = 0
        for start in range(current_n):
            v = start
            while (v != current_root and component[v] == -1
                   and visited[v] != start):
                visited[v] = start
                v = parent[v]
            if v != current_root and component[v] == -1:
                component[v] = cycle_count
                u = parent[v]
                while u != v:
                    component[u] = cycle_count
                    u = parent[u]
                cycle_count += 1

        if cycle_count == 0:
            selected = {incoming_edge[v] for v in range(current_n)
                        if v != current_root}
            break

        next_n = cycle_count
        for v in range(current_n):
            if component[v] == -1:
                component[v] = next_n
                next_n += 1
        next_edges = []
        next_to_old = []
        for old_edge, (u, v, cost, original) in enumerate(current_edges):
            a = component[u]
            b = component[v]
            if a != b:
                next_edges.append((a, b, cost - incoming_cost[v], original))
                next_to_old.append(old_edge)
        levels.append((current_edges, current_root, incoming_edge, next_to_old))
        current_edges = next_edges
        current_n = next_n
        current_root = component[current_root]

    while levels:
        old_edges, old_root, incoming_edge, next_to_old = levels.pop()
        selected_old = {incoming_edge[v] for v in range(len(incoming_edge))
                        if v != old_root}
        for edge_id in selected:
            old_edge = next_to_old[edge_id]
            target = old_edges[old_edge][1]
            if target != old_root:
                selected_old.discard(incoming_edge[target])
            selected_old.add(old_edge)
        selected = selected_old
        current_edges = old_edges

    original_ids = [current_edges[edge_id][3] for edge_id in selected]
    original_ids.sort()
    return sum(edges[edge_id][2] for edge_id in original_ids), original_ids

