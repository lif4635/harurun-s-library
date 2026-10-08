"""Range actions and range products with lazy propagation.

Use this when one update affects every element in a half-open interval and
interval aggregates are also required.  The caller supplies the monoid, how an
action changes an aggregate, and how newer and older actions compose.
"""

class LazySegTree:
    __slots__ = ('n', 'size', 'log', 'data', 'lazy', 'pending', 'length', 'op', 'identity', 'mapping', 'composition', 'id')

    def __init__(self, op, identity, mapping, composition, id, values):
        if isinstance(values, int):
            n = values
            values = [identity] * n
        else:
            values = list(values)
            n = len(values)
        size = 1 << (n - 1).bit_length() if n else 1
        data = [identity] * (size << 1)
        data[size:size + n] = values
        length = [0] * (size << 1)
        for index in range(size, size + n):
            length[index] = 1
        for node in range(size - 1, 0, -1):
            data[node] = op(data[node << 1], data[node << 1 | 1])
            length[node] = length[node << 1] + length[node << 1 | 1]
        self.n = n
        self.size = size
        self.log = size.bit_length() - 1
        self.data = data
        self.lazy = [id] * size
        self.pending = bytearray(size)
        self.length = length
        self.op = op
        self.identity = identity
        self.mapping = mapping
        self.composition = composition
        self.id = id

    def _update(self, node):
        self.data[node] = self.op(self.data[node << 1], self.data[node << 1 | 1])

    def _all_apply(self, node, action):
        self.data[node] = self.mapping(action, self.data[node], self.length[node])
        if node < self.size:
            if self.pending[node]:
                self.lazy[node] = self.composition(action, self.lazy[node])
            else:
                self.lazy[node] = action
                self.pending[node] = 1

    def _push(self, node):
        if self.pending[node]:
            action = self.lazy[node]
            self._all_apply(node << 1, action)
            self._all_apply(node << 1 | 1, action)
            self.lazy[node] = self.id
            self.pending[node] = 0

    def set(self, index, value):
        node = index + self.size
        for shift in range(self.log, 0, -1):
            self._push(node >> shift)
        self.data[node] = value
        for shift in range(1, self.log + 1):
            self._update(node >> shift)

    def add(self, index, value):
        """indexの現在値をop(value, current)で置き換える。O(log N)。"""
        node = index + self.size
        for shift in range(self.log, 0, -1):
            self._push(node >> shift)
        self.data[node] = self.op(value, self.data[node])
        for shift in range(1, self.log + 1):
            self._update(node >> shift)

    def get(self, index):
        node = index + self.size
        for shift in range(self.log, 0, -1):
            self._push(node >> shift)
        return self.data[node]

    def tolist(self):
        """遅延作用を反映した現在の要素列をlistで返す。O(N)。"""
        for node in range(1, self.size):
            self._push(node)
        return self.data[self.size:self.size + self.n]

    def __str__(self):
        return str(self.tolist())

    def __repr__(self):
        return 'LazySegTree(%r)' % self.tolist()

    def prod(self, left, right):
        if left == right:
            return self.identity
        left += self.size
        right += self.size
        for shift in range(self.log, 0, -1):
            if left >> shift << shift != left:
                self._push(left >> shift)
            if right >> shift << shift != right:
                self._push(right - 1 >> shift)
        first = self.identity
        second = self.identity
        op = self.op
        data = self.data
        while left < right:
            if left & 1:
                first = op(first, data[left])
                left += 1
            if right & 1:
                right -= 1
                second = op(data[right], second)
            left >>= 1
            right >>= 1
        return op(first, second)
    query = prod

    def apply(self, left, right=None, action=None):
        if action is None:
            index = left
            action = right
            node = index + self.size
            for shift in range(self.log, 0, -1):
                self._push(node >> shift)
            self._all_apply(node, action)
            for shift in range(1, self.log + 1):
                self._update(node >> shift)
            return
        if left == right:
            return
        left += self.size
        right += self.size
        original_left = left
        original_right = right
        for shift in range(self.log, 0, -1):
            if left >> shift << shift != left:
                self._push(left >> shift)
            if right >> shift << shift != right:
                self._push(right - 1 >> shift)
        while left < right:
            if left & 1:
                self._all_apply(left, action)
                left += 1
            if right & 1:
                right -= 1
                self._all_apply(right, action)
            left >>= 1
            right >>= 1
        left = original_left
        right = original_right
        for shift in range(1, self.log + 1):
            if left >> shift << shift != left:
                self._update(left >> shift)
            if right >> shift << shift != right:
                self._update(right - 1 >> shift)
    range_apply = apply

    def all_prod(self):
        return self.data[1]

    def max_right(self, left, predicate):
        if left == self.n:
            return self.n
        node = left + self.size
        for shift in range(self.log, 0, -1):
            self._push(node >> shift)
        value = self.identity
        while True:
            while not node & 1:
                node >>= 1
            merged = self.op(value, self.data[node])
            if not predicate(merged):
                while node < self.size:
                    self._push(node)
                    node <<= 1
                    merged = self.op(value, self.data[node])
                    if predicate(merged):
                        value = merged
                        node += 1
                return min(node - self.size, self.n)
            value = merged
            node += 1
            if node & -node == node:
                break
        return self.n

    def min_left(self, right, predicate):
        if right == 0:
            return 0
        node = right + self.size
        for shift in range(self.log, 0, -1):
            self._push(node - 1 >> shift)
        value = self.identity
        while True:
            node -= 1
            while node > 1 and node & 1:
                node >>= 1
            merged = self.op(self.data[node], value)
            if not predicate(merged):
                while node < self.size:
                    self._push(node)
                    node = node << 1 | 1
                    merged = self.op(self.data[node], value)
                    if predicate(merged):
                        value = merged
                        node -= 1
                return max(0, node + 1 - self.size)
            value = merged
            if node & -node == node:
                break
        return 0
import sys

def op(first, second):
    return ((first[0] + second[0]) % 998244353, first[1] + second[1])

def mapping(action, value, length):
    (a, b) = action
    return ((a * value[0] + b * value[1]) % 998244353, value[1])

def composition(new, old):
    (a, b) = new
    (c, d) = old
    return (a * c % 998244353, (a * d + b) % 998244353)
read = sys.stdin.buffer.readline
(n, q) = map(int, read().split())
queries = [list(map(int, read().split())) for _ in range(q)]
points = sorted({point for row in queries for point in row[1:3]})
index = {value: i for (i, value) in enumerate(points)}
values = [(0, points[i + 1] - points[i]) for i in range(len(points) - 1)]
tree = LazySegTree(op, (0, 0), mapping, composition, (1, 0), values)
answer = []
for row in queries:
    (left, right) = (index[row[1]], index[row[2]])
    if row[0] == 0:
        tree.apply(left, right, (row[3], row[4]))
    else:
        answer.append(tree.prod(left, right)[0])
print('\n'.join(map(str, answer)))
