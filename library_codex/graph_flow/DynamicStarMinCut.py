"""固定の無向グラフに中心を加え、中心の辺重みを更新しながら全域最小カットを求める。"""

from library_codex.graph_flow.ExtremeVertexSet import extreme_vertex_tree
from library_codex.tree.HeavyLightDecomposition import HeavyLightDecomposition


class DynamicStarMinCut:
    __slots__ = ("n", "values", "children", "hld", "size", "data", "lazy")

    def __init__(self, n, edges, values=None):
        values = [0] * n if values is None else list(values)
        if len(values) != n or any(value < 0 for value in values):
            raise ValueError("expected n nonnegative star weights")
        children, boundary = extreme_vertex_tree(n, edges)
        hld = HeavyLightDecomposition(children, 2 * n - 2)
        total = values + [0] * (n - 1)
        for v in range(n, 2 * n - 1):
            u, w = children[v]
            total[v] = total[u] + total[w]
        size = 1 << (2 * n - 2).bit_length()
        data = [float("inf")] * (size * 2)
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
        start, end = left, right - 1
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
            raise IndexError("invalid vertex")
        if weight < 0:
            raise ValueError("weight must be nonnegative")
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
        return "DynamicStarMinCut(" + str(self.tolist()) + ")"
