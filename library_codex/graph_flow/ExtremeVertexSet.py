"""非負重み無向グラフの極小なカット候補を含む二分木を作る。"""

from heapq import heapify, heappop, heappush


def extreme_vertex_tree(n, edges):
    """全extreme setを部分木として含むchildrenと各部分木の境界重みを返す。"""
    if n < 1:
        raise ValueError("n must be positive")
    graph = [{} for _ in range(n)]
    for u, v, weight in edges:
        if not 0 <= u < n or not 0 <= v < n:
            raise ValueError("invalid vertex")
        if weight < 0:
            raise ValueError("weights must be nonnegative")
        if u != v and weight:
            graph[u][v] = graph[u].get(v, 0) + weight
            graph[v][u] = graph[v].get(u, 0) + weight
    degree = [sum(row.values()) for row in graph]
    boundary = degree[:]
    children = [()] * n
    if not any(degree):
        children.extend((2 * i, 2 * i + 1) for i in range(n - 1))
        return children, [0] * (2 * n - 1)
    representative = list(range(n))
    active = list(range(n))
    visited = [0] * n
    for phase in range(1, n):
        costs = degree[:]
        heap = [(degree[v], v) for v in active]
        heapify(heap)
        last = -1
        for _ in range(len(active)):
            while True:
                _, vertex = heappop(heap)
                if visited[vertex] != phase:
                    break
            visited[vertex] = phase
            previous, last = last, vertex
            for other, weight in graph[vertex].items():
                if visited[other] != phase:
                    costs[other] -= weight
                    heappush(heap, (costs[other], other))
        u, v = previous, last
        if len(graph[u]) > len(graph[v]):
            u, v = v, u
        children.append((representative[u], representative[v]))
        degree[v] += degree[u] - 2 * graph[u].get(v, 0)
        boundary.append(degree[v])
        for other, weight in graph[u].items():
            del graph[other][u]
            if other != v:
                graph[other][v] = graph[other].get(v, 0) + weight
                graph[v][other] = graph[v].get(other, 0) + weight
        graph[u] = {}
        representative[v] = n + phase - 1
        active.remove(u)
    return children, boundary
