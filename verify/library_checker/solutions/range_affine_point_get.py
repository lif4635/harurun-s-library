"""Range actions with point queries.

Use this lighter structure when updates cover intervals but only individual
positions are queried.  It intentionally stores no range aggregate.
"""

class DualSegTree:
    __slots__ = ('n', 'size', 'log', 'value', 'lazy', 'pending', 'mapping', 'composition', 'id')

    def __init__(self, mapping, composition, id, values):
        if isinstance(values, int):
            values = [None] * values
        else:
            values = list(values)
        n = len(values)
        size = 1 << (n - 1).bit_length() if n else 1
        self.n = n
        self.size = size
        self.log = size.bit_length() - 1
        self.value = values
        self.lazy = [id] * size
        self.pending = bytearray(size)
        self.mapping = mapping
        self.composition = composition
        self.id = id

    def _apply_node(self, node, action):
        if self.pending[node]:
            self.lazy[node] = self.composition(action, self.lazy[node])
        else:
            self.lazy[node] = action
            self.pending[node] = 1

    def _push(self, node):
        if not self.pending[node]:
            return
        action = self.lazy[node]
        if node << 1 < self.size:
            self._apply_node(node << 1, action)
            self._apply_node(node << 1 | 1, action)
        else:
            left = (node << 1) - self.size
            right = left + 1
            if left < self.n:
                self.value[left] = self.mapping(action, self.value[left])
            if right < self.n:
                self.value[right] = self.mapping(action, self.value[right])
        self.lazy[node] = self.id
        self.pending[node] = 0

    def apply(self, left, right, action):
        if left == right:
            return
        left += self.size
        right += self.size
        for shift in range(self.log, 0, -1):
            if left & (1 << shift) - 1:
                self._push(left >> shift)
            if right & (1 << shift) - 1:
                self._push(right - 1 >> shift)
        while left < right:
            if left & 1:
                if left >= self.size:
                    index = left - self.size
                    self.value[index] = self.mapping(action, self.value[index])
                else:
                    self._apply_node(left, action)
                left += 1
            if right & 1:
                right -= 1
                if right >= self.size:
                    index = right - self.size
                    self.value[index] = self.mapping(action, self.value[index])
                else:
                    self._apply_node(right, action)
            left >>= 1
            right >>= 1
    range_apply = apply

    def get(self, index):
        node = index + self.size
        for shift in range(self.log, 0, -1):
            self._push(node >> shift)
        return self.value[index]

    def set(self, index, value):
        self.get(index)
        self.value[index] = value

    def tolist(self):
        """遅延作用を反映した現在の要素列をlistで返す。O(N)。"""
        for node in range(1, self.size):
            self._push(node)
        return self.value[:]

    def __str__(self):
        return str(self.tolist())

    def __repr__(self):
        return 'DualSegTree(%r)' % self.tolist()
import sys

def mapping(action, value):
    (a, b) = action
    return (a * value + b) % 998244353

def composition(new, old):
    (a, b) = new
    (c, d) = old
    return (a * c % 998244353, (a * d + b) % 998244353)

def solve():
    data = iter(map(int, sys.stdin.buffer.read().split()))
    (n, q) = (next(data), next(data))
    tree = DualSegTree(mapping, composition, (1, 0), [next(data) for _ in range(n)])
    answer = []
    for _ in range(q):
        if next(data) == 0:
            (l, r, a, b) = (next(data), next(data), next(data), next(data))
            tree.apply(l, r, (a, b))
        else:
            answer.append(str(tree.get(next(data))))
    print('\n'.join(answer))
if __name__ == '__main__':
    solve()
