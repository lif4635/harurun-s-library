"""辺を1本ずつ追加し、最小全域森の重みと採用辺を保つ。"""

class IncrementalMSF:
    """整数重みの辺を追加するたびに、森から外れた辺の追加順IDを返す。"""
    __slots__ = ('n', 'weight', 'components', '_count', '_parent', '_size', '_weights', '_ids', '_from', '_to')

    def __init__(self, n):
        if n < 0:
            raise ValueError('n must be nonnegative')
        self.n = n
        self.weight = 0
        self.components = n
        self._count = 0
        self._parent = [-1] * n
        self._size = [1] * n
        self._weights = [0] * n
        self._ids = [-1] * n
        self._from = [0] * n
        self._to = [0] * n

    def _promote(self, node):
        (parent, size, weights) = (self._parent, self._size, self._weights)
        (ids, first, second) = (self._ids, self._from, self._to)
        p = parent[node]
        g = parent[p]
        parent[node] = g
        size[p] -= size[node]
        if g < 0 or weights[node] < weights[p] or (weights[node] == weights[p] and ids[node] < ids[p]):
            parent[p] = node
            size[node] += size[p]
            (weights[node], weights[p]) = (weights[p], weights[node])
            (ids[node], ids[p]) = (ids[p], ids[node])
            (first[node], first[p]) = (first[p], first[node])
            (second[node], second[p]) = (second[p], second[node])

    def _calibrate(self, node):
        (parent, size) = (self._parent, self._size)
        while parent[node] >= 0:
            if 3 * size[node] > 2 * size[parent[node]]:
                self._promote(node)
            else:
                node = parent[node]

    def _perch(self, node):
        while self._parent[node] >= 0:
            self._promote(node)

    def add(self, u, v, weight):
        """辺を追加し、外れた辺のIDを返す。新規接続なら-1、不採用なら今回のID。"""
        if not 0 <= u < self.n or not 0 <= v < self.n:
            raise ValueError('vertex index out of range')
        edge_id = self._count
        self._count += 1
        if u == v:
            return edge_id
        self._calibrate(u)
        self._calibrate(v)
        self._perch(u)
        self._perch(v)
        (parent, size, weights) = (self._parent, self._size, self._weights)
        (first, second) = (u, v)
        if parent[u] == v:
            if weight >= weights[u]:
                return edge_id
            removed = self._ids[u]
            self.weight -= weights[u]
        else:
            if size[u] > size[v]:
                (u, v) = (v, u)
            parent[u] = v
            size[v] += size[u]
            self.components -= 1
            removed = -1
        weights[u] = weight
        self._ids[u] = edge_id
        self._from[u] = first
        self._to[u] = second
        self.weight += weight
        return removed

    def edges(self):
        """現在採用中の辺を、(追加順ID, u, v, 重み)のlistとしてID順に返す。"""
        return sorted(((edge_id, self._from[i], self._to[i], self._weights[i]) for (i, edge_id) in enumerate(self._ids) if edge_id >= 0))

    def __repr__(self):
        return f'IncrementalMSF(n={self.n}, edges={self.edges()!r})'

    def __str__(self):
        return str(self.edges())
import sys

def main():
    input = sys.stdin.buffer.readline
    (n, m) = map(int, input().split())
    forest = IncrementalMSF(n)
    answers = []
    for _ in range(m):
        (u, v, weight) = map(int, input().split())
        answers.append(str(forest.add(u, v, weight)))
    sys.stdout.write(' '.join(answers) + '\n')
if __name__ == '__main__':
    main()
