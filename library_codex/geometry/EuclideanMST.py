"""平面上の点をユークリッド距離の合計が最小になる木で結ぶ。"""

from library_codex.geometry.Delaunay import delaunay_edges


def euclidean_mst(points):
    """最小全域木の辺を入力点の番号の組で返す。時間O(N log N)、追加空間O(N)。"""
    edges = delaunay_edges(points)
    x, y = [p[0] for p in points], [p[1] for p in points]
    edges.sort(key=lambda e: (x[e[0]] - x[e[1]]) ** 2 + (y[e[0]] - y[e[1]]) ** 2)
    parent = [-1] * len(points)
    result = []
    for u, v in edges:
        a, b = u, v
        while parent[a] >= 0:
            if parent[parent[a]] >= 0:
                parent[a] = parent[parent[a]]
            a = parent[a]
        while parent[b] >= 0:
            if parent[parent[b]] >= 0:
                parent[b] = parent[parent[b]]
            b = parent[b]
        if a == b:
            continue
        if parent[a] > parent[b]:
            a, b = b, a
        parent[a] += parent[b]
        parent[b] = a
        result.append((u, v))
        if len(result) == len(points) - 1:
            break
    return result
