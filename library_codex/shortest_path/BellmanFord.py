"""負辺を含むグラフの最短路と負閉路の影響を求める。"""

INF = float("inf")

def bellman_ford(vertex_count, edges, start=0):
    distance = [INF] * vertex_count
    previous = [-1] * vertex_count
    distance[start] = 0
    for _ in range(vertex_count - 1):
        changed = False
        for first, second, weight, *_ in edges:
            if distance[first] != INF:
                value = distance[first] + weight
                if value < distance[second]:
                    distance[second] = value
                    previous[second] = first
                    changed = True
        if not changed:
            break
    negative = bytearray(vertex_count)
    for _ in range(vertex_count):
        changed = False
        for first, second, weight, *_ in edges:
            if distance[first] == INF:
                continue
            if distance[first] + weight < distance[second] or negative[first]:
                if not negative[second]:
                    changed = True
                negative[second] = 1
                distance[second] = -INF
        if not changed:
            break
    return distance, previous, negative

