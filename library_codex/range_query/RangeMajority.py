"""区間の過半数を占める値と出現回数。点更新にも対応する。"""

from bisect import bisect_left
from random import getrandbits


class RangeMajority:
    __slots__ = ("n", "size", "candidate", "balance", "positions",
                 "_roots", "_left", "_right", "_parent", "_sizes", "_priority")

    def __init__(self, values):
        values = list(values)
        self.n = n = len(values)
        self.size = size = 1 << (n - 1).bit_length() if n else 1
        self.candidate = [None] * (size << 1)
        self.balance = [0] * (size << 1)
        self.candidate[size:size + n] = values
        self.balance[size:size + n] = [1] * n
        self.positions = positions = {}
        for index, value in enumerate(values):
            positions.setdefault(value, []).append(index)
        for node in range(size - 1, 0, -1):
            self._update(node)
        self._roots = None
        self._left = self._right = self._parent = self._sizes = self._priority = None

    def _update(self, node):
        candidates, counts = self.candidate, self.balance
        a, b = node << 1, node << 1 | 1
        x, y = counts[a], counts[b]
        if candidates[a] == candidates[b]:
            candidates[node], counts[node] = candidates[a], x + y
        elif x >= y:
            candidates[node], counts[node] = candidates[a], x - y
        else:
            candidates[node], counts[node] = candidates[b], y - x

    def _enable_updates(self):
        n = self.n
        left, right, parent = [-1] * n, [-1] * n, [-1] * n
        sizes = [1] * n
        priority = [getrandbits(32) for _ in range(n)]
        roots = {}
        for value, indices in self.positions.items():
            stack = []
            for node in indices:
                last = -1
                while stack and priority[stack[-1]] > priority[node]:
                    last = stack.pop()
                if stack:
                    right[stack[-1]] = node
                    parent[node] = stack[-1]
                if last >= 0:
                    left[node] = last
                    parent[last] = node
                stack.append(node)
            roots[value] = stack[0]
        order = list(roots.values())
        for node in order:
            if left[node] >= 0:
                order.append(left[node])
            if right[node] >= 0:
                order.append(right[node])
        for node in reversed(order):
            if parent[node] >= 0:
                sizes[parent[node]] += sizes[node]
        self._roots, self._priority = roots, priority
        self._left, self._right, self._parent, self._sizes = left, right, parent, sizes
        self.positions = None

    def _rotate(self, node, value):
        left, right, parent, sizes = self._left, self._right, self._parent, self._sizes
        p = parent[node]
        grand = parent[p]
        if left[p] == node:
            middle = right[node]
            right[node], left[p] = p, middle
        else:
            middle = left[node]
            left[node], right[p] = p, middle
        if middle >= 0:
            parent[middle] = p
        parent[p], parent[node] = node, grand
        if grand < 0:
            self._roots[value] = node
        elif left[grand] == p:
            left[grand] = node
        else:
            right[grand] = node
        sizes[node] = sizes[p]
        sizes[p] = 1 + (sizes[left[p]] if left[p] >= 0 else 0) + (sizes[right[p]] if right[p] >= 0 else 0)

    def set(self, index, value):
        if not 0 <= index < self.n:
            raise IndexError("index out of range")
        hash(value)
        old = self.candidate[self.size + index]
        if old == value:
            return
        if self._roots is None:
            self._enable_updates()
        left, right, parent, sizes = self._left, self._right, self._parent, self._sizes
        priority, roots = self._priority, self._roots
        while left[index] >= 0 or right[index] >= 0:
            a, b = left[index], right[index]
            child = a if b < 0 or (a >= 0 and priority[a] < priority[b]) else b
            self._rotate(child, old)
        p = parent[index]
        if p < 0:
            del roots[old]
        elif left[p] == index:
            left[p] = -1
        else:
            right[p] = -1
        while p >= 0:
            sizes[p] -= 1
            p = parent[p]
        parent[index], sizes[index] = -1, 1
        node = roots.get(value, -1)
        if node < 0:
            roots[value] = index
        else:
            while True:
                sizes[node] += 1
                child = left[node] if index < node else right[node]
                if child < 0:
                    if index < node:
                        left[node] = index
                    else:
                        right[node] = index
                    parent[index] = node
                    break
                node = child
            while parent[index] >= 0 and priority[index] < priority[parent[index]]:
                self._rotate(index, value)
        node = self.size + index
        self.candidate[node] = value
        node >>= 1
        while node:
            self._update(node)
            node >>= 1

    def _rank(self, value, index):
        node = self._roots.get(value, -1)
        left, right, sizes = self._left, self._right, self._sizes
        result = 0
        while node >= 0:
            if node >= index:
                node = left[node]
            else:
                result += 1 + (sizes[left[node]] if left[node] >= 0 else 0)
                node = right[node]
        return result

    def count(self, value, left, right):
        if not 0 <= left <= right <= self.n:
            raise IndexError("invalid half-open range")
        if self._roots is not None:
            return self._rank(value, right) - self._rank(value, left)
        row = self.positions.get(value, ())
        return bisect_left(row, right) - bisect_left(row, left)

    def majority(self, left, right):
        if not 0 <= left <= right <= self.n:
            raise IndexError("invalid half-open range")
        first, last = left + self.size, right + self.size
        value, count = None, 0
        candidates, counts = self.candidate, self.balance
        while first < last:
            if first & 1:
                other, amount = candidates[first], counts[first]
                if value == other:
                    count += amount
                elif count >= amount:
                    count -= amount
                else:
                    value, count = other, amount - count
                first += 1
            if last & 1:
                last -= 1
                other, amount = candidates[last], counts[last]
                if value == other:
                    count += amount
                elif count >= amount:
                    count -= amount
                else:
                    value, count = other, amount - count
            first >>= 1
            last >>= 1
        if not count:
            return None
        count = self.count(value, left, right)
        return (value, count) if count * 2 > right - left else None

    def is_majority(self, value, left, right):
        return self.count(value, left, right) * 2 > right - left

    def tolist(self):
        return self.candidate[self.size:self.size + self.n]

    def __str__(self):
        return str(self.tolist())

    def __repr__(self):
        return "RangeMajority(%r)" % self.tolist()
