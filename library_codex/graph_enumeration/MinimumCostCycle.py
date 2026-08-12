"""Minimum-cost directed cycle with nonnegative edge weights."""

from heapq import heappop, heappush


def minimum_cost_cycle(n, edges):
    """Return ``(cost, vertices, edge_ids)`` for a cheapest directed cycle.

    ``vertices`` repeats its first vertex at the end.  ``None`` is returned
    when no directed cycle exists.  Complexity is ``O(V E log V)``.
    """
    edges = list(edges)
    graph = [[] for _ in range(n)]
    incoming = [[] for _ in range(n)]
    for edge_id, (first, second, weight) in enumerate(edges):
        if not 0 <= first < n or not 0 <= second < n:
            raise IndexError("edge endpoint is out of range")
        if weight < 0:
            raise ValueError("edge weights must be nonnegative")
        graph[first].append((second, weight, edge_id))
        incoming[second].append((first, weight, edge_id))

    best = None
    infinity = float("inf")
    for start in range(n):
        distance = [infinity] * n
        previous_vertex = [-1] * n
        previous_edge = [-1] * n
        distance[start] = 0
        heap = [(0, start)]
        while heap:
            current, vertex = heappop(heap)
            if current != distance[vertex]:
                continue
            for other, weight, edge_id in graph[vertex]:
                candidate = current + weight
                if candidate < distance[other]:
                    distance[other] = candidate
                    previous_vertex[other] = vertex
                    previous_edge[other] = edge_id
                    heappush(heap, (candidate, other))
        for last, weight, closing_edge in incoming[start]:
            if distance[last] == infinity:
                continue
            cost = distance[last] + weight
            if best is not None and cost >= best[0]:
                continue
            reverse_vertices = []
            reverse_edges = []
            vertex = last
            while vertex != start:
                reverse_vertices.append(vertex)
                reverse_edges.append(previous_edge[vertex])
                vertex = previous_vertex[vertex]
            vertices = [start] + list(reversed(reverse_vertices)) + [start]
            edge_ids = list(reversed(reverse_edges)) + [closing_edge]
            best = cost, vertices, edge_ids
    return best
