"""無向グラフに含まれる三角形を重複なく列挙する。"""

def enumerate_triangles(n, edges, callback=None):
    """Enumerate triangles in O(n + m sqrt(m)) time.

    Each item is ``(u, v, w, uv_edge, uw_edge, vw_edge)``.  If ``callback`` is
    given it is invoked for each item and the count is returned; otherwise a
    list is returned.
    """
    degree = [0] * n
    for u, v in edges:
        degree[u] += 1
        degree[v] += 1
    high = [[] for _ in range(n)]
    for edge_id, (u, v) in enumerate(edges):
        if (degree[u], u) < (degree[v], v):
            high[u].append((v, edge_id))
        else:
            high[v].append((u, edge_id))
    marked = [-1] * n
    result = [] if callback is None else None
    count = 0
    for u in range(n):
        for v, edge_id in high[u]:
            marked[v] = edge_id
        for v, uv_edge in high[u]:
            for w, vw_edge in high[v]:
                uw_edge = marked[w]
                if uw_edge != -1:
                    item = (u, v, w, uv_edge, uw_edge, vw_edge)
                    if callback is None:
                        result.append(item)
                    else:
                        callback(*item)
                    count += 1
        for v, _ in high[u]:
            marked[v] = -1
    return result if callback is None else count

