"""無向グラフを、指定した始点から終点へ全頂点を通れる向きに並べる。"""


def st_numbering(graph, source, target):
    """Return vertex ranks with source first and target last, or None."""
    n = len(graph)
    if not 0 <= source < n or not 0 <= target < n:
        raise IndexError("source or target is outside the graph")
    if n == 1:
        return [0]
    if source == target:
        return None
    if hasattr(graph, "start"):
        if graph.directed:
            raise ValueError("st-numbering requires an undirected graph")
        start, to = graph.start, graph.to
    else:
        start = [0]
        to = []
        for row in graph:
            to.extend(row)
            start.append(len(to))
    preorder = [-1] * n
    low = [0] * n
    parent = [-1] * n
    cursor = start[:-1]
    preorder[source] = 0
    preorder[target] = low[target] = 1
    order = [source, target]
    v = target
    while v >= 0:
        if cursor[v] == start[v + 1]:
            p = parent[v]
            if p >= 0 and low[v] < low[p]:
                low[p] = low[v]
            v = p
            continue
        u = to[cursor[v]]
        cursor[v] += 1
        if not 0 <= u < n:
            raise IndexError("neighbor is outside the graph")
        if preorder[u] < 0:
            parent[u] = v
            preorder[u] = low[u] = len(order)
            order.append(u)
            v = u
        elif preorder[u] < low[v]:
            low[v] = preorder[u]
    if len(order) != n:
        return None
    previous = [-1] * n
    following = [-1] * n
    following[source] = target
    previous[target] = source
    negative = bytearray(n)
    negative[source] = 1
    for v in order[2:]:
        p = parent[v]
        if negative[order[low[v]]]:
            q = previous[p]
            if q < 0:
                return None
            following[q] = v
            following[v] = p
            previous[v] = q
            previous[p] = v
            negative[p] = 0
        else:
            q = following[p]
            if q < 0:
                return None
            following[p] = v
            following[v] = q
            previous[v] = p
            previous[q] = v
            negative[p] = 1
    rank = [-1] * n
    v = source
    for i in range(n):
        if v < 0:
            return None
        rank[v] = i
        v = following[v]
    if rank[target] != n - 1:
        return None
    for v in range(n):
        earlier = v == source
        later = v == target
        for i in range(start[v], start[v + 1]):
            value = rank[to[i]]
            earlier |= value < rank[v]
            later |= rank[v] < value
        if not earlier or not later:
            return None
    return rank
