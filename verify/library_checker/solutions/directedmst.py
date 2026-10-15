"""指定rootから全頂点へ到達する有向全域木の最小費用と辺番号を求める。"""

def minimum_cost_arborescence(n, root, edges):
    """最小費用と採用した辺番号の昇順listを返す。構築不能ならNone。"""
    if n == 0:
        return (0, [])
    if not 0 <= root < n:
        raise IndexError('root out of range')
    m = len(edges)
    cost = [edge[2] for edge in edges]
    best = [-1] * n
    for (edge_id, (source, target, value)) in enumerate(edges):
        if source != target and target != root:
            previous = best[target]
            if previous == -1 or value < cost[previous]:
                best[target] = edge_id
    if any((best[v] == -1 for v in range(n) if v != root)):
        return None
    state = [0] * n
    state[root] = -1
    cyclic = False
    for start in range(n):
        if state[start]:
            continue
        vertex = start
        stamp = start + 1
        while state[vertex] == 0:
            state[vertex] = stamp
            vertex = edges[best[vertex]][0]
        if state[vertex] == stamp:
            cyclic = True
            break
    if not cyclic:
        selected = sorted((best[v] for v in range(n) if v != root))
        return (sum((cost[i] for i in selected)), selected)
    lazy = [0] * m
    child = [-1] * m
    sibling = [-1] * m
    heaps = [-1] * (2 * n)
    parent = [-1] * (2 * n)
    contracted = [-1] * (2 * n)
    chosen = [-1] * (2 * n)
    used = [0] * (2 * n)

    def find(vertex):
        while parent[vertex] != -1:
            above = parent[vertex]
            if parent[above] == -1:
                return above
            parent[vertex] = parent[above]
            vertex = parent[above]
        return vertex

    def meld(a, b):
        if a == -1:
            return b
        if b == -1:
            return a
        if cost[a] + lazy[a] > cost[b] + lazy[b]:
            (a, b) = (b, a)
        lazy[b] -= lazy[a]
        sibling[b] = child[a]
        child[a] = b
        return a

    def pop(heap):
        current = child[heap]
        offset = lazy[heap]
        pairs = []
        while current != -1:
            a = current
            b = sibling[a]
            lazy[a] += offset
            sibling[a] = -1
            if b == -1:
                pairs.append(a)
                break
            current = sibling[b]
            lazy[b] += offset
            sibling[b] = -1
            pairs.append(meld(a, b))
        result = -1
        for a in reversed(pairs):
            result = meld(a, result)
        return result
    for (edge_id, (source, target, _)) in enumerate(edges):
        if source != target and target != root:
            heaps[target] = meld(heaps[target], edge_id)
    used[root] = -1
    size = n
    for start in range(n):
        if used[start]:
            continue
        stamp = start + 1
        vertex = start
        while not used[vertex] or used[vertex] == stamp:
            if used[vertex] == stamp:
                merged = size
                size += 1
                while vertex != merged:
                    heap = heaps[vertex]
                    lazy[heap] = -cost[chosen[vertex]]
                    heaps[merged] = meld(heaps[merged], heap)
                    parent[vertex] = contracted[vertex] = merged
                    vertex = find(edges[chosen[vertex]][0])
                vertex = merged
            used[vertex] = stamp
            heap = heaps[vertex]
            while heap != -1 and find(edges[heap][0]) == vertex:
                heap = pop(heap)
            heaps[vertex] = heap
            if heap == -1:
                return None
            chosen[vertex] = heap
            vertex = find(edges[heap][0])
    done = bytearray(size)
    done[root] = 1
    selected = []
    for vertex in range(size - 1, -1, -1):
        if done[vertex]:
            continue
        edge_id = chosen[vertex]
        selected.append(edge_id)
        target = edges[edge_id][1]
        while target != -1 and (not done[target]):
            done[target] = 1
            target = contracted[target]
    selected.sort()
    return (sum((cost[edge_id] for edge_id in selected)), selected)
import sys
data = list(map(int, sys.stdin.buffer.read().split()))
(n, m, root) = data[:3]
edges = list(zip(data[3::3], data[4::3], data[5::3]))
(cost, selected) = minimum_cost_arborescence(n, root, edges)
parent = [root] * n
for edge_id in selected:
    (source, target, _) = edges[edge_id]
    parent[target] = source
print(cost)
print(*parent)
