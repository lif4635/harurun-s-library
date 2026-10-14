"""辺の追加削除と頂点・連結成分への加算、成分和を先読みで処理する。"""

class OfflineDynamicSum:
    """操作を登録し、solveでqueryの答えを登録順に返す。"""
    __slots__ = ('values', 'bits', 'mask', 'active', 'intervals', 'events', 'queries')

    def __init__(self, values):
        self.values = list(values)
        self.bits = max(1, (len(self.values) - 1).bit_length())
        self.mask = (1 << self.bits) - 1
        self.active = {}
        self.intervals = []
        self.events = []
        self.queries = 0

    def _vertex(self, vertex):
        if not 0 <= vertex < len(self.values):
            raise IndexError('vertex out of range')

    def _edge(self, u, v):
        self._vertex(u)
        self._vertex(v)
        if u > v:
            (u, v) = (v, u)
        return u << self.bits | v

    def add_edge(self, u, v):
        edge = self._edge(u, v)
        if edge in self.active:
            raise ValueError('edge already exists')
        self.active[edge] = len(self.events)

    def remove_edge(self, u, v):
        edge = self._edge(u, v)
        if edge not in self.active:
            raise ValueError('edge does not exist')
        left = self.active.pop(edge)
        right = len(self.events)
        if left < right:
            self.intervals.append((left, right, edge))

    def add(self, vertex, delta):
        self._vertex(vertex)
        self.events.append((0, vertex, delta))

    def add_component(self, vertex, delta):
        self._vertex(vertex)
        self.events.append((1, vertex, delta))

    def query(self, vertex):
        self._vertex(vertex)
        self.events.append((2, vertex, 0))
        index = self.queries
        self.queries += 1
        return index

    def solve(self):
        q = len(self.events)
        if not q:
            return []
        size = 1 << (q - 1).bit_length()
        buckets = [None] * (2 * size)
        intervals = self.intervals + [(left, q, edge) for (edge, left) in self.active.items()]
        for (left, right, edge) in intervals:
            left += size
            right = 2 * size if right == q else right + size
            while left < right:
                if left & 1:
                    if buckets[left] is None:
                        buckets[left] = [edge]
                    else:
                        buckets[left].append(edge)
                    left += 1
                if right & 1:
                    right -= 1
                    if buckets[right] is None:
                        buckets[right] = [edge]
                    else:
                        buckets[right].append(edge)
                left >>= 1
                right >>= 1
        n = len(self.values)
        parent = [-1] * n
        total = self.values.copy()
        lazy = [0] * n
        cancel = [0] * n
        bits = self.bits
        mask = self.mask
        size_bits = max(1, n.bit_length())
        size_mask = (1 << size_bits) - 1
        events = self.events
        history = []
        stack = [1]
        answer = []
        while stack:
            node = stack.pop()
            if node < 0:
                checkpoint = ~node
                while len(history) > checkpoint:
                    entry = history.pop()
                    (y, count) = (entry >> size_bits, entry & size_mask)
                    x = parent[y]
                    delta = lazy[x] - cancel[y]
                    total[y] += count * delta
                    lazy[y] += delta
                    total[x] -= total[y]
                    parent[x] += count
                    parent[y] = -count
                continue
            if node >= size + q:
                continue
            stack.append(~len(history))
            edges = buckets[node]
            if edges is not None:
                for edge in edges:
                    (x, y) = (edge >> bits, edge & mask)
                    while parent[x] >= 0:
                        x = parent[x]
                    while parent[y] >= 0:
                        y = parent[y]
                    if x == y:
                        continue
                    if parent[x] > parent[y]:
                        (x, y) = (y, x)
                    history.append(y << size_bits | -parent[y])
                    parent[x] += parent[y]
                    parent[y] = x
                    total[x] += total[y]
                    cancel[y] = lazy[x]
            if node < size:
                stack.append(2 * node + 1)
                stack.append(2 * node)
                continue
            (kind, vertex, delta) = events[node - size]
            if kind == 0:
                while True:
                    total[vertex] += delta
                    if parent[vertex] < 0:
                        break
                    vertex = parent[vertex]
            else:
                while parent[vertex] >= 0:
                    vertex = parent[vertex]
                if kind == 1:
                    total[vertex] -= parent[vertex] * delta
                    lazy[vertex] += delta
                else:
                    answer.append(total[vertex])
        return answer
import sys

def main():
    read = sys.stdin.buffer.readline
    (n, q) = map(int, read().split())
    tree = OfflineDynamicSum(list(map(int, read().split())))
    for _ in range(n - 1):
        (u, v) = map(int, read().split())
        tree.add_edge(u, v)
    for _ in range(q):
        query = list(map(int, read().split()))
        if query[0] == 0:
            (_, u, v, w, x) = query
            tree.remove_edge(u, v)
            tree.add_edge(w, x)
        elif query[0] == 1:
            (_, v, p, x) = query
            tree.remove_edge(v, p)
            tree.add_component(v, x)
            tree.add_edge(v, p)
        else:
            (_, v, p) = query
            tree.remove_edge(v, p)
            tree.query(v)
            tree.add_edge(v, p)
    sys.stdout.write('\n'.join(map(str, tree.solve())) + '\n')
if __name__ == '__main__':
    main()
