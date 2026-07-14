from library_codex.data_structure.RadixHeap import RadixHeap


def dijkstra_radix_heap(edge, start=0, goal=None):
    n = len(edge)
    dist = [-1] * n
    dist[start] = 0
    que = RadixHeap()
    que.push(0, start)
    while que:
        d, u = que.pop()
        if dist[u] != d:
            continue
        if u == goal:
            return d
        for v, w in edge[u]:
            nd = d + w
            if dist[v] < 0 or nd < dist[v]:
                dist[v] = nd
                que.push(nd, v)
    return dist if goal is None else -1


def dijkstra_radix_heap_restore(edge, start=0):
    n = len(edge)
    dist = [-1] * n
    parent = [-1] * n
    dist[start] = 0
    que = RadixHeap()
    que.push(0, start)
    while que:
        d, u = que.pop()
        if dist[u] != d:
            continue
        for v, w in edge[u]:
            nd = d + w
            if dist[v] < 0 or nd < dist[v]:
                dist[v] = nd
                parent[v] = u
                que.push(nd, v)
    return dist, parent


def restore_path(parent, goal):
    path = []
    while goal != -1:
        path.append(goal)
        goal = parent[goal]
    path.reverse()
    return path
