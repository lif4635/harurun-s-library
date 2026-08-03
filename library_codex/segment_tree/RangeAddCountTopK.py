"""区間一括加算後の値を大きい順に個数付きで上位k件集約する構造。"""

from dataclasses import dataclass

@dataclass(order=True)
class TopKNode:
    x: object
    f: object

class RangeAddCountTopK:
    __slots__ = ("length", "size", "k", "tree", "lazy", "minimum", "zero")

    def __init__(self, length, k, fill_value=0, fill_frequency=1,
                 minimum=None, zero=0):
        if length < 0 or k < 0:
            raise ValueError("length and k must be nonnegative")
        size = 1
        while size < length:
            size <<= 1
        self.length = length
        self.size = size
        self.k = k
        self.minimum = minimum
        self.zero = zero
        tree = [[] for _ in range(size << 1)]
        for index in range(length):
            tree[size + index] = [TopKNode(fill_value, fill_frequency)]
        self.tree = tree
        self.lazy = [0] * size
        for node in range(size - 1, 0, -1):
            tree[node] = self._merge(tree[node << 1], tree[node << 1 | 1])

    def _merge(self, first, second):
        result = []
        left = right = 0
        while len(result) < self.k and (left < len(first) or right < len(second)):
            if right == len(second) or (
                left < len(first) and first[left].x > second[right].x
            ):
                result.append(first[left])
                left += 1
            elif left == len(first) or second[right].x > first[left].x:
                result.append(second[right])
                right += 1
            else:
                result.append(TopKNode(
                    first[left].x, first[left].f + second[right].f
                ))
                left += 1
                right += 1
        return result

    def _apply(self, node, delta):
        self.tree[node] = [TopKNode(value.x + delta, value.f)
                           for value in self.tree[node]]
        if node < self.size:
            self.lazy[node] += delta

    def _push(self, node):
        delta = self.lazy[node]
        if delta:
            self._apply(node << 1, delta)
            self._apply(node << 1 | 1, delta)
            self.lazy[node] = 0

    def range_add(self, left, right, delta):
        if not 0 <= left <= right <= self.length:
            raise IndexError("invalid half-open range")
        stack = [(1, 0, self.size, 0)]
        while stack:
            node, lower, upper, phase = stack.pop()
            if right <= lower or upper <= left:
                continue
            if left <= lower and upper <= right:
                self._apply(node, delta)
                continue
            if phase:
                self.tree[node] = self._merge(
                    self.tree[node << 1], self.tree[node << 1 | 1]
                )
                continue
            self._push(node)
            middle = (lower + upper) >> 1
            stack.append((node, lower, upper, 1))
            stack.append((node << 1 | 1, middle, upper, 0))
            stack.append((node << 1, lower, middle, 0))

    rangeAdd = range_add

    def range_top_k(self, left, right):
        if not 0 <= left <= right <= self.length:
            raise IndexError("invalid half-open range")
        result = []
        stack = [(1, 0, self.size)]
        while stack:
            node, lower, upper = stack.pop()
            if right <= lower or upper <= left:
                continue
            if left <= lower and upper <= right:
                result = self._merge(result, self.tree[node])
                continue
            self._push(node)
            middle = (lower + upper) >> 1
            stack.append((node << 1 | 1, middle, upper))
            stack.append((node << 1, lower, middle))
        if self.minimum is not None:
            result.extend([TopKNode(self.minimum, self.zero)]
                          * (self.k - len(result)))
        return result

    rangeTopK = range_top_k

    def top_k(self):
        result = self.tree[1][:]
        if self.minimum is not None:
            result.extend([TopKNode(self.minimum, self.zero)]
                          * (self.k - len(result)))
        return result

    topK = top_k
