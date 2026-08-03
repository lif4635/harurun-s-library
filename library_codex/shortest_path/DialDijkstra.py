"""非負整数重みが小さいグラフの最短路をbucketで求める。"""

def dial_dijkstra(graph, starts, max_weight, restore=False):
    """Dijkstra with circular buckets for integer weights in [0,max_weight]."""
    n = len(graph)
    if isinstance(starts, int):
        starts = [starts]
    width = max_weight + 1
    if width <= 0:
        raise ValueError("max_weight must be nonnegative")
    buckets = [[] for _ in range(width)]
    inf = float("inf")
    distance = [inf] * n
    parent = [-1] * n
    active = 0
    for start in starts:
        if distance[start] != 0:
            distance[start] = 0
            buckets[0].append(start)
            active += 1
    current = 0
    while active:
        bucket = buckets[current % width]
        if not bucket:
            current += 1
            continue
        v = bucket.pop()
        active -= 1
        if distance[v] != current:
            continue
        for to, weight in graph[v]:
            if not 0 <= weight <= max_weight or int(weight) != weight:
                raise ValueError("edge weight must be an integer in range")
            nxt = current + weight
            if nxt < distance[to]:
                distance[to] = nxt
                parent[to] = v
                buckets[nxt % width].append(to)
                active += 1
    return (distance, parent) if restore else distance

