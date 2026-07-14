from dataclasses import dataclass
from math import isqrt


@dataclass(frozen=True)
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


class LazyKDTree:
    __slots__ = (
        "n", "root", "left", "right", "parent", "xmin", "xmax", "ymin",
        "ymax", "point_x", "point_y", "point_value", "size", "value", "lazy", "pending", "position", "combine",
        "identity", "mapping", "composition", "lazy_identity",
    )

    def __init__(self, xs, ys, weights, combine=lambda a, b: a + b,
                 identity=0,
                 mapping=lambda value, action, size: value + action * size,
                 composition=lambda old, new: old + new,
                 lazy_identity=0):
        if not (len(xs) == len(ys) == len(weights)):
            raise ValueError("coordinate and weight lengths differ")
        n = len(xs)
        self.n = n
        self.combine = combine
        self.identity = identity
        self.mapping = mapping
        self.composition = composition
        self.lazy_identity = lazy_identity
        self.left = []
        self.right = []
        self.parent = []
        self.xmin = []
        self.xmax = []
        self.ymin = []
        self.ymax = []
        self.point_x = []
        self.point_y = []
        self.point_value = []
        self.size = []
        self.value = []
        self.lazy = []
        self.pending = bytearray()
        self.position = [-1] * n
        if n == 0:
            self.root = -1
            return
        points = [(xs[i], ys[i], weights[i], i) for i in range(n)]
        tasks = [(points, 0, -1, 0)]
        root = -1
        while tasks:
            subset, depth, parent, side = tasks.pop()
            subset.sort(key=lambda point: point[depth & 1])
            middle = len(subset) >> 1
            x, y, weight, original = subset[middle]
            node = len(self.left)
            self.left.append(-1)
            self.right.append(-1)
            self.parent.append(parent)
            self.xmin.append(x)
            self.xmax.append(x)
            self.ymin.append(y)
            self.ymax.append(y)
            self.point_x.append(x)
            self.point_y.append(y)
            self.point_value.append(weight)
            self.size.append(1)
            self.value.append(weight)
            self.lazy.append(lazy_identity)
            self.pending.append(0)
            self.position[original] = node
            if parent < 0:
                root = node
            elif side == 0:
                self.left[parent] = node
            else:
                self.right[parent] = node
            if middle + 1 < len(subset):
                tasks.append((subset[middle + 1:], depth + 1, node, 1))
            if middle:
                tasks.append((subset[:middle], depth + 1, node, 0))
        self.root = root
        for node in range(n - 1, -1, -1):
            self._pull(node)

    def _pull(self, node):
        total = 1
        value = self.point_value[node]
        self.xmin[node] = self.xmax[node] = self.point_x[node]
        self.ymin[node] = self.ymax[node] = self.point_y[node]
        for child in (self.left[node], self.right[node]):
            if child >= 0:
                total += self.size[child]
                self.xmin[node] = min(self.xmin[node], self.xmin[child])
                self.xmax[node] = max(self.xmax[node], self.xmax[child])
                self.ymin[node] = min(self.ymin[node], self.ymin[child])
                self.ymax[node] = max(self.ymax[node], self.ymax[child])
                value = self.combine(value, self.value[child])
        self.size[node] = total
        self.value[node] = value

    def _apply(self, node, action):
        self.value[node] = self.mapping(
            self.value[node], action, self.size[node]
        )
        self.point_value[node] = self.mapping(
            self.point_value[node], action, 1
        )
        if self.pending[node]:
            self.lazy[node] = self.composition(self.lazy[node], action)
        else:
            self.lazy[node] = action
            self.pending[node] = 1

    def _push(self, node):
        if not self.pending[node]:
            return
        action = self.lazy[node]
        for child in (self.left[node], self.right[node]):
            if child >= 0:
                self._apply(child, action)
        self.lazy[node] = self.lazy_identity
        self.pending[node] = 0

    def _outside(self, node, left, right, down, up):
        return (self.xmax[node] < left or right <= self.xmin[node]
                or self.ymax[node] < down or up <= self.ymin[node])

    def _inside(self, node, left, right, down, up):
        return (left <= self.xmin[node] and self.xmax[node] < right
                and down <= self.ymin[node] and self.ymax[node] < up)

    def update(self, left, right, down, up, action):
        if self.root < 0:
            return
        stack = [(self.root, 0)]
        while stack:
            node, phase = stack.pop()
            if self._outside(node, left, right, down, up):
                continue
            if self._inside(node, left, right, down, up):
                self._apply(node, action)
                continue
            if phase:
                self._pull(node)
                continue
            self._push(node)
            x = self.point_x[node]
            y = self.point_y[node]
            if left <= x < right and down <= y < up:
                self.point_value[node] = self.mapping(
                    self.point_value[node], action, 1
                )
            stack.append((node, 1))
            for child in (self.right[node], self.left[node]):
                if child >= 0:
                    stack.append((child, 0))

    def set(self, index, value):
        node = self.position[index]
        if node < 0:
            raise IndexError("point index out of range")
        path = []
        current = node
        while current >= 0:
            path.append(current)
            current = self.parent[current]
        for current in reversed(path):
            self._push(current)
        self.point_value[node] = value
        for current in path:
            self._pull(current)

    def query(self, left, right, down, up):
        if self.root < 0:
            return self.identity
        result = self.identity
        stack = [self.root]
        while stack:
            node = stack.pop()
            if self._outside(node, left, right, down, up):
                continue
            if self._inside(node, left, right, down, up):
                result = self.combine(result, self.value[node])
                continue
            self._push(node)
            x = self.point_x[node]
            y = self.point_y[node]
            if left <= x < right and down <= y < up:
                result = self.combine(result, self.point_value[node])
            stack.extend(child for child in (self.left[node], self.right[node])
                         if child >= 0)
        return result


class SortableSegmentTree:
    """Sortable sequence with point update and monoid range product."""

    __slots__ = ("n", "keys", "values", "op", "identity", "block",
                 "forward", "reverse")

    def __init__(self, keys, values, op=lambda a, b: a + b, identity=0,
                 block_size=None):
        if len(keys) != len(values):
            raise ValueError("key and value lengths differ")
        self.n = len(keys)
        self.keys = list(keys)
        self.values = list(values)
        self.op = op
        self.identity = identity
        self.block = block_size or max(32, isqrt(max(1, self.n)) + 1)
        count = (self.n + self.block - 1) // self.block
        self.forward = [identity] * count
        self.reverse = [identity] * count
        for index in range(count):
            self._rebuild(index)

    def _rebuild(self, block):
        left = block * self.block
        right = min(self.n, left + self.block)
        forward = reverse = self.identity
        for index in range(left, right):
            forward = self.op(forward, self.values[index])
        for index in range(right - 1, left - 1, -1):
            reverse = self.op(reverse, self.values[index])
        self.forward[block] = forward
        self.reverse[block] = reverse

    def update(self, index, key, value):
        self.keys[index] = key
        self.values[index] = value
        self._rebuild(index // self.block)

    set = update

    def query(self, left, right):
        result = self.identity
        while left < right and left % self.block:
            result = self.op(result, self.values[left])
            left += 1
        while left + self.block <= right:
            result = self.op(result, self.forward[left // self.block])
            left += self.block
        while left < right:
            result = self.op(result, self.values[left])
            left += 1
        return result

    def sort(self, left, right, reverse=False):
        pairs = list(zip(self.keys[left:right], self.values[left:right]))
        pairs.sort(key=lambda pair: pair[0], reverse=reverse)
        for offset, (key, value) in enumerate(pairs, left):
            self.keys[offset] = key
            self.values[offset] = value
        if left < right:
            first = left // self.block
            last = (right - 1) // self.block
            for block in range(first, last + 1):
                self._rebuild(block)
