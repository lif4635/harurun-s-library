"""各辺が含まれる長さ4のcycle数を数える。"""

def count_c4_per_edge(n, edges, weight=None):
    """For each edge, sum products of the other three edges over all C4s.

    With omitted weights this is simply the number of (not necessarily induced)
    4-cycles containing each edge.  Runs in O(n + m sqrt(m)) on a simple graph.
    """
    m = len(edges)
    if weight is None:
        weight = [1] * m
    elif len(weight) != m:
        raise ValueError("weight length must equal the number of edges")
    degree = [0] * n
    for u, v in edges:
        degree[u] += 1
        degree[v] += 1
    order = sorted(range(n), key=lambda v: degree[v])
    rank = [0] * n
    for i, v in enumerate(order):
        rank[v] = i
    transformed = []
    for u, v in edges:
        u = rank[u]
        v = rank[v]
        if u < v:
            u, v = v, u
        transformed.append((u, v))

    start = [0] * n
    for v in range(n - 1):
        start[v + 1] = start[v] + degree[order[v]]
    end = start[:]
    edge_id = [0] * (m << 1)
    to = [0] * (m << 1)
    for e, (v, w) in enumerate(transformed):
        i = end[v]
        edge_id[i] = e
        to[i] = w
        end[v] = i + 1
    directed_end = end[:]
    for v in range(n):
        for i in range(start[v], directed_end[v]):
            e = edge_id[i]
            w = to[i]
            j = end[w]
            edge_id[j] = e
            to[j] = v
            end[w] = j + 1

    path_sum = [0] * n
    answer = [0] * m
    for v in range(n - 1, -1, -1):
        for i in range(start[v], end[v]):
            evw = edge_id[i]
            w = to[i]
            end[w] -= 1
            for j in range(start[w], end[w]):
                ewx = edge_id[j]
                x = to[j]
                path_sum[x] += weight[evw] * weight[ewx]
        for i in range(start[v], end[v]):
            evw = edge_id[i]
            w = to[i]
            for j in range(start[w], end[w]):
                ewx = edge_id[j]
                x = to[j]
                value = path_sum[x] - weight[evw] * weight[ewx]
                answer[evw] += value * weight[ewx]
                answer[ewx] += value * weight[evw]
        for i in range(start[v], end[v]):
            w = to[i]
            for j in range(start[w], end[w]):
                path_sum[to[j]] = 0
    return answer

