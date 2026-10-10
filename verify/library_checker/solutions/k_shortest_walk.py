"""非負辺重みの有向グラフで、頂点や辺を再訪できるwalkの長さを昇順に求める。"""
from heapq import heappop, heappush

def k_shortest_walks(vertex_count, edges, source, target, k):
    """Return up to k walk costs, retaining equal costs with multiplicity."""
    if k <= 0:
        return []
    n = vertex_count
    if not 0 <= source < n or not 0 <= target < n:
        raise IndexError('source or target is outside the graph')
    edge_from = []
    edge_to = []
    weight = []
    start = [0] * (n + 1)
    reverse_start = [0] * (n + 1)
    for (u, v, cost) in edges:
        if not 0 <= u < n or not 0 <= v < n:
            raise IndexError('an edge endpoint is outside the graph')
        if cost < 0:
            raise ValueError('edge weights must be nonnegative')
        edge_from.append(u)
        edge_to.append(v)
        weight.append(cost)
        start[u + 1] += 1
        reverse_start[v + 1] += 1
    for v in range(n):
        start[v + 1] += start[v]
        reverse_start[v + 1] += reverse_start[v]
    m = len(weight)
    forward = [0] * m
    reverse = [0] * m
    cursor = start[:-1]
    reverse_cursor = reverse_start[:-1]
    for e in range(m):
        (u, v) = (edge_from[e], edge_to[e])
        forward[cursor[u]] = e
        reverse[reverse_cursor[v]] = e
        cursor[u] += 1
        reverse_cursor[v] += 1
    inf = float('inf')
    distance = [inf] * n
    tree_edge = [-1] * n
    distance[target] = 0
    queue = [(0, target)]
    order = []
    while queue:
        (dist, v) = heappop(queue)
        if distance[v] != dist:
            continue
        order.append(v)
        for i in range(reverse_start[v], reverse_start[v + 1]):
            e = reverse[i]
            u = edge_from[e]
            candidate = dist + weight[e]
            if candidate < distance[u]:
                distance[u] = candidate
                tree_edge[u] = e
                heappush(queue, (candidate, u))
    if distance[source] == inf:
        return []
    if k == 1:
        return [distance[source]]
    del reverse, reverse_start, reverse_cursor, cursor, edge_from
    key = [0]
    destination = [0]
    left = [0]
    right = [0]
    rank = [0]
    roots = [0] * n

    def meld(a, b, persistent):
        path = []
        while a and b:
            if key[b] < key[a]:
                (a, b) = (b, a)
            path.append(a)
            a = right[a]
        root = a or b
        while path:
            node = path.pop()
            (l, r) = (left[node], root)
            if rank[l] < rank[r]:
                (l, r) = (r, l)
            if persistent:
                key.append(key[node])
                destination.append(destination[node])
                left.append(l)
                right.append(r)
                rank.append(rank[r] + 1)
                root = len(key) - 1
            else:
                left[node] = l
                right[node] = r
                rank[node] = rank[r] + 1
                root = node
        return root
    for v in order:
        root = 0
        chosen = tree_edge[v]
        for i in range(start[v], start[v + 1]):
            e = forward[i]
            u = edge_to[e]
            if e == chosen or distance[u] == inf:
                continue
            key.append(weight[e] + distance[u] - distance[v])
            destination.append(u)
            left.append(0)
            right.append(0)
            rank.append(1)
            root = meld(root, len(key) - 1, False)
        if chosen >= 0:
            inherited = roots[edge_to[chosen]]
            root = meld(inherited, root, True) if root else inherited
        roots[v] = root
    answer = [distance[source]]
    root = roots[source]
    candidates = [(answer[0] + key[root], root)] if root else []
    while candidates and len(answer) < k:
        (cost, node) = heappop(candidates)
        answer.append(cost)
        base = cost - key[node]
        child = left[node]
        if child:
            heappush(candidates, (base + key[child], child))
        child = right[node]
        if child:
            heappush(candidates, (base + key[child], child))
        root = roots[destination[node]]
        if root:
            heappush(candidates, (cost + key[root], root))
    return answer
import sys
read = sys.stdin.buffer.readline
(n, m, source, target, k) = map(int, read().split())
edges = [tuple(map(int, read().split())) for _ in range(m)]
answer = k_shortest_walks(n, edges, source, target, k)
sys.stdout.write('\n'.join(map(str, answer + [-1] * (k - len(answer)))) + '\n')
