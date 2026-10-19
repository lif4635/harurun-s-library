"""非負重み無向グラフの極小なカット候補を含む二分木を作る。"""
from heapq import heapify, heappop, heappush

def extreme_vertex_tree(n, edges):
    """全extreme setを部分木として含むchildrenと各部分木の境界重みを返す。"""
    if n < 1:
        raise ValueError('n must be positive')
    graph = [{} for _ in range(n)]
    for (u, v, weight) in edges:
        if not 0 <= u < n or not 0 <= v < n:
            raise ValueError('invalid vertex')
        if weight < 0:
            raise ValueError('weights must be nonnegative')
        if u != v and weight:
            graph[u][v] = graph[u].get(v, 0) + weight
            graph[v][u] = graph[v].get(u, 0) + weight
    degree = [sum(row.values()) for row in graph]
    boundary = degree[:]
    children = [()] * n
    if not any(degree):
        children.extend(((2 * i, 2 * i + 1) for i in range(n - 1)))
        return (children, [0] * (2 * n - 1))
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
                (_, vertex) = heappop(heap)
                if visited[vertex] != phase:
                    break
            visited[vertex] = phase
            (previous, last) = (last, vertex)
            for (other, weight) in graph[vertex].items():
                if visited[other] != phase:
                    costs[other] -= weight
                    heappush(heap, (costs[other], other))
        (u, v) = (previous, last)
        if len(graph[u]) > len(graph[v]):
            (u, v) = (v, u)
        children.append((representative[u], representative[v]))
        degree[v] += degree[u] - 2 * graph[u].get(v, 0)
        boundary.append(degree[v])
        for (other, weight) in graph[u].items():
            del graph[other][u]
            if other != v:
                graph[other][v] = graph[other].get(v, 0) + weight
                graph[v][other] = graph[v].get(other, 0) + weight
        graph[u] = {}
        representative[v] = n + phase - 1
        active.remove(u)
    return (children, boundary)

class HeavyLightDecomposition:
    __slots__ = ('n', 'parent', 'depth', 'size', 'head', 'tin', 'tout', 'rev')

    def __init__(self, edge, root=0):
        n = len(edge)
        assert 0 <= root < n
        parent = [-1] * n
        depth = [0] * n
        order = [root]
        for u in order:
            for v in edge[u]:
                if v != parent[u]:
                    parent[v] = u
                    depth[v] = depth[u] + 1
                    order.append(v)
        size = [1] * n
        heavy = [-1] * n
        for u in reversed(order):
            best = 0
            for v in edge[u]:
                if parent[v] == u:
                    sv = size[v]
                    size[u] += sv
                    if sv > best:
                        best = sv
                        heavy[u] = v
        head = [0] * n
        tin = [0] * n
        rev = [0] * n
        stack = [(root, root)]
        timer = 0
        while stack:
            (u, h) = stack.pop()
            while u != -1:
                head[u] = h
                tin[u] = timer
                rev[timer] = u
                timer += 1
                hu = heavy[u]
                for v in edge[u]:
                    if parent[v] == u and v != hu:
                        stack.append((v, v))
                u = hu
        self.n = n
        self.parent = parent
        self.depth = depth
        self.size = size
        self.head = head
        self.tin = tin
        self.tout = [tin[v] + size[v] for v in range(n)]
        self.rev = rev

    def lca(self, u, v):
        parent = self.parent
        depth = self.depth
        head = self.head
        while head[u] != head[v]:
            if depth[head[u]] > depth[head[v]]:
                u = parent[head[u]]
            else:
                v = parent[head[v]]
        return u if depth[u] < depth[v] else v

    def dist(self, u, v):
        w = self.lca(u, v)
        return self.depth[u] + self.depth[v] - (self.depth[w] << 1)

    def kth_ancestor(self, v, k):
        if k < 0 or self.depth[v] < k:
            return -1
        parent = self.parent
        depth = self.depth
        head = self.head
        tin = self.tin
        while depth[v] - depth[head[v]] < k:
            k -= depth[v] - depth[head[v]] + 1
            v = parent[head[v]]
        return self.rev[tin[v] - k]

    def jump(self, u, v, k):
        w = self.lca(u, v)
        up = self.depth[u] - self.depth[w]
        distance = up + self.depth[v] - self.depth[w]
        if k < 0 or distance < k:
            return -1
        if k <= up:
            return self.kth_ancestor(u, k)
        return self.kth_ancestor(v, distance - k)

    def next_on_path(self, u, v):
        if u == v:
            return -1
        return self.jump(u, v, 1)
    nxt = next_on_path

    def vertices_on_path(self, u, v):
        distance = self.dist(u, v)
        return [self.jump(u, v, k) for k in range(distance + 1)]

    def subtree(self, v, edge=False):
        return (self.tin[v] + edge, self.tout[v])

    def path(self, u, v, edge=False):
        res = []
        parent = self.parent
        depth = self.depth
        head = self.head
        tin = self.tin
        while head[u] != head[v]:
            if depth[head[u]] > depth[head[v]]:
                res.append((tin[head[u]], tin[u] + 1))
                u = parent[head[u]]
            else:
                res.append((tin[head[v]], tin[v] + 1))
                v = parent[head[v]]
        if depth[u] > depth[v]:
            (l, r) = (tin[v] + edge, tin[u] + 1)
        else:
            (l, r) = (tin[u] + edge, tin[v] + 1)
        if l < r:
            res.append((l, r))
        return res

    def path_ordered(self, u, v, edge=False):
        up = []
        down = []
        parent = self.parent
        depth = self.depth
        head = self.head
        tin = self.tin
        while head[u] != head[v]:
            if depth[head[u]] > depth[head[v]]:
                up.append((tin[head[u]], tin[u] + 1, True))
                u = parent[head[u]]
            else:
                down.append((tin[head[v]], tin[v] + 1, False))
                v = parent[head[v]]
        if depth[u] > depth[v]:
            (l, r) = (tin[v] + edge, tin[u] + 1)
            if l < r:
                up.append((l, r, True))
        else:
            (l, r) = (tin[u] + edge, tin[v] + 1)
            if l < r:
                down.append((l, r, False))
        up.extend(reversed(down))
        return up

    def index(self, v):
        return self.tin[v]

    def vertex(self, i):
        return self.rev[i]
HLD = HeavyLightDecomposition
'固定の無向グラフに中心を加え、中心の辺重みを更新しながら全域最小カットを求める。'

class DynamicStarMinCut:
    __slots__ = ('n', 'values', 'children', 'hld', 'size', 'data', 'lazy')

    def __init__(self, n, edges, values=None):
        values = [0] * n if values is None else list(values)
        if len(values) != n or any((value < 0 for value in values)):
            raise ValueError('expected n nonnegative star weights')
        (children, boundary) = extreme_vertex_tree(n, edges)
        hld = HeavyLightDecomposition(children, 2 * n - 2)
        total = values + [0] * (n - 1)
        for v in range(n, 2 * n - 1):
            (u, w) = children[v]
            total[v] = total[u] + total[w]
        size = 1 << (2 * n - 2).bit_length()
        data = [float('inf')] * (size * 2)
        for v in range(2 * n - 1):
            data[size + hld.tin[v]] = boundary[v] + total[v]
        for v in range(size - 1, 0, -1):
            data[v] = min(data[v * 2], data[v * 2 + 1])
        self.n = n
        self.values = values
        self.children = children
        self.hld = hld
        self.size = size
        self.data = data
        self.lazy = [0] * size

    def _add(self, left, right, delta):
        size = self.size
        data = self.data
        lazy = self.lazy
        left += size
        right += size
        (start, end) = (left, right - 1)
        while left < right:
            if left & 1:
                data[left] += delta
                if left < size:
                    lazy[left] += delta
                left += 1
            if right & 1:
                right -= 1
                data[right] += delta
                if right < size:
                    lazy[right] += delta
            left >>= 1
            right >>= 1
        start >>= 1
        end >>= 1
        while start:
            data[start] = min(data[start * 2], data[start * 2 + 1]) + lazy[start]
            if end != start:
                data[end] = min(data[end * 2], data[end * 2 + 1]) + lazy[end]
            start >>= 1
            end >>= 1

    def set(self, vertex, weight):
        """中心とvertexの辺重みを置き換え、更新後の全域最小カット重みを返す。"""
        if not 0 <= vertex < self.n:
            raise IndexError('invalid vertex')
        if weight < 0:
            raise ValueError('weight must be nonnegative')
        delta = weight - self.values[vertex]
        self.values[vertex] = weight
        if delta:
            head = self.hld.head
            tin = self.hld.tin
            parent = self.hld.parent
            while vertex != -1:
                top = head[vertex]
                self._add(tin[top], tin[vertex] + 1, delta)
                vertex = parent[top]
        return self.data[1]

    def min_cut(self):
        """現在の全域最小カット重みを整数で返す。O(1)。"""
        return self.data[1]

    def cut(self):
        """最小カットのうち中心を含まない側の元頂点を昇順listで返す。O(N)。"""
        v = 1
        while v < self.size:
            v *= 2
            if self.data[v] > self.data[v + 1]:
                v += 1
        stack = [self.hld.rev[v - self.size]]
        included = bytearray(self.n)
        while stack:
            vertex = stack.pop()
            if vertex < self.n:
                included[vertex] = 1
            else:
                stack.extend(self.children[vertex])
        return [v for v in range(self.n) if included[v]]

    def tolist(self):
        """中心から各元頂点への辺重みを頂点順のlistで返す。O(N)。"""
        return self.values[:]

    def __str__(self):
        return str(self.tolist())

    def __repr__(self):
        return 'DynamicStarMinCut(' + str(self.tolist()) + ')'
import sys

def main():
    read = sys.stdin.buffer.readline
    (n, m, q) = map(int, read().split())
    weights = list(map(int, read().split()))
    edges = [tuple(map(int, read().split())) for _ in range(m)]
    graph = DynamicStarMinCut(n, edges, weights)
    output = []
    for _ in range(q):
        (vertex, weight) = map(int, read().split())
        output.append(str(graph.set(vertex, weight)))
    sys.stdout.write('\n'.join(output))
if __name__ == '__main__':
    main()
