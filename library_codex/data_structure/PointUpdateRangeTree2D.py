"""登録済み二次元点の重みを更新し、半開矩形和をonlineで求めるrange tree。"""

from bisect import bisect_left

class PointUpdateRangeTree2D:
    """Offline-coordinate point update / rectangle monoid fold range tree."""

    __slots__ = ("points", "n", "ys", "sizes", "data", "op", "identity",
                 "update")

    def __init__(self, points=(), op=lambda first, second: first + second,
                 identity=0, update=None):
        self.points = list(points)
        self.n = 0
        self.ys = []
        self.sizes = []
        self.data = []
        self.op = op
        self.identity = identity
        self.update = update or op

    def add_point(self, x, y):
        if self.n:
            raise RuntimeError("points must be registered before build")
        self.points.append((x, y))

    def build(self):
        points = sorted(set(self.points))
        self.points = points
        n = len(points)
        self.n = n
        ys = [[] for _ in range(max(2, n << 1))]
        for index, (_, y) in enumerate(points):
            node = index + n
            while node:
                ys[node].append(y)
                node >>= 1
        sizes = [1] * len(ys)
        data = [None] * len(ys)
        for node in range(1, len(ys)):
            ys[node] = sorted(set(ys[node]))
            size = 1 << (len(ys[node]) - 1).bit_length() if ys[node] else 1
            sizes[node] = size
            data[node] = [self.identity] * (size << 1)
        self.ys = ys
        self.sizes = sizes
        self.data = data
        return self

    def _xid(self, x):
        return bisect_left(self.points, (x,))

    def _inner_update(self, node, y, value, replace):
        index = bisect_left(self.ys[node], y)
        if index == len(self.ys[node]) or self.ys[node][index] != y:
            raise KeyError("point was not registered")
        index += self.sizes[node]
        row = self.data[node]
        row[index] = value if replace else self.update(row[index], value)
        index >>= 1
        while index:
            row[index] = self.op(row[index << 1], row[index << 1 | 1])
            index >>= 1

    def add(self, x, y, value):
        index = bisect_left(self.points, (x, y))
        if index == self.n or self.points[index] != (x, y):
            raise KeyError("point was not registered")
        node = index + self.n
        while node:
            self._inner_update(node, y, value, False)
            node >>= 1

    def set(self, x, y, value):
        index = bisect_left(self.points, (x, y))
        if index == self.n or self.points[index] != (x, y):
            raise KeyError("point was not registered")
        # Recover the old leaf value and apply its replacement at every ancestor.
        leaf = index + self.n
        y_index = bisect_left(self.ys[leaf], y) + self.sizes[leaf]
        old = self.data[leaf][y_index]
        if self.update is not self.op:
            raise ValueError("set is only available through a custom replacement strategy")
        # For additive groups users should call add(delta); generic monoids cannot remove old.
        if old != self.identity:
            raise ValueError("generic set cannot replace an existing nonidentity value")
        node = leaf
        while node:
            self._inner_update(node, y, value, False)
            node >>= 1

    def _inner_query(self, node, bottom, top):
        left = bisect_left(self.ys[node], bottom) + self.sizes[node]
        right = bisect_left(self.ys[node], top) + self.sizes[node]
        row = self.data[node]
        left_value = self.identity
        right_value = self.identity
        while left < right:
            if left & 1:
                left_value = self.op(left_value, row[left])
                left += 1
            if right & 1:
                right -= 1
                right_value = self.op(row[right], right_value)
            left >>= 1
            right >>= 1
        return self.op(left_value, right_value)

    def query(self, left, bottom, right, top):
        first = self._xid(left) + self.n
        last = self._xid(right) + self.n
        left_value = self.identity
        right_value = self.identity
        while first < last:
            if first & 1:
                left_value = self.op(
                    left_value, self._inner_query(first, bottom, top)
                )
                first += 1
            if last & 1:
                last -= 1
                right_value = self.op(
                    self._inner_query(last, bottom, top), right_value
                )
            first >>= 1
            last >>= 1
        return self.op(left_value, right_value)

    sum = query
    prod = query
