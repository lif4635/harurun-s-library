"""非負重みの無向グラフから、頂点間距離の最大値が最小の全域木を選ぶ。"""

from heapq import heappop, heappush


def minimum_diameter_spanning_tree(n, edges):
    """(最小直径, 入力辺番号の昇順list)を返す。非連結ならNone。"""
    if n < 0:
        raise ValueError("n must be nonnegative")
    edges = list(edges)
    graph = [[] for _ in range(n)]
    bound = 1
    for eid, (u, v, weight) in enumerate(edges):
        if not 0 <= u < n or not 0 <= v < n or weight < 0:
            raise ValueError("invalid endpoint or negative weight")
        if u != v:
            graph[u].append((v, weight, eid))
            graph[v].append((u, weight, eid))
            bound += weight
    if n <= 1:
        return 0, []
    distances = []
    best = 2 * bound
    center = 0
    center_edge = -1
    offset = 0
    for root in range(n):
        dist = [bound] * n
        dist[root] = 0
        heap = [(0, root)]
        while heap:
            cost, u = heappop(heap)
            if cost != dist[u]:
                continue
            for v, weight, _ in graph[u]:
                candidate = cost + weight
                if candidate < dist[v]:
                    dist[v] = candidate
                    heappush(heap, (candidate, v))
        eccentricity = max(dist)
        if eccentricity == bound:
            return None
        if 2 * eccentricity < best:
            best = 2 * eccentricity
            center = root
        distances.append(dist)
    for u in range(n):
        first = distances[u]
        order = sorted(range(n), key=first.__getitem__, reverse=True)
        for v, weight, eid in graph[u]:
            if u >= v or weight > first[v]:
                continue
            second = distances[v]
            farthest = second[order[0]]
            for x in order[1:]:
                if second[x] > farthest:
                    candidate = farthest + first[x] + weight
                    if candidate < best:
                        best = candidate
                        center_edge = eid
                        center = u
                        offset = farthest + weight - first[x]
                    farthest = second[x]
    dist = [2 * bound] * n
    parent = [-1] * n
    if center_edge < 0:
        dist[center] = 0
        heap = [(0, center)]
        selected = []
    else:
        u, v, weight = edges[center_edge]
        if u != center:
            u, v = v, u
        dist[u] = offset
        dist[v] = 2 * weight - offset
        heap = [(dist[u], u), (dist[v], v)]
        if heap[0] > heap[1]:
            heap.reverse()
        selected = [center_edge]
    while heap:
        cost, u = heappop(heap)
        if cost != dist[u]:
            continue
        for v, weight, eid in graph[u]:
            candidate = cost + 2 * weight
            if candidate < dist[v]:
                dist[v] = candidate
                parent[v] = eid
                heappush(heap, (candidate, v))
    selected.extend(eid for eid in parent if eid >= 0)
    selected.sort()
    return best, selected
