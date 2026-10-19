"""登録済みの二次元点に、矩形内の一次変換・矩形和・点ごとの有効化と置換を行う。"""


_BUCKET_SIZE = 16
_ADAPTIVE_AXES = True


class RectangleAffineSum:
    """固定座標の点の重みを法付きで管理する。Noneの重みはまだ有効でない点を表す。"""

    __slots__ = ("n", "mod", "_position", "_xmin", "_xmax", "_ymin", "_ymax",
                 "_count", "_sum", "_a", "_b", "_lo", "_hi", "_xs", "_ys", "_values", "_order")

    def __init__(self, points, mod=998244353):
        if mod < 1:
            raise ValueError("mod must be positive")
        points = list(points)
        self.n = n = len(points)
        self.mod = mod
        size = 2 << (max(1, (n + _BUCKET_SIZE - 1) // _BUCKET_SIZE) - 1).bit_length()
        self._position = [0] * n
        self._xmin = [0] * size
        self._xmax = [0] * size
        self._ymin = [0] * size
        self._ymax = [0] * size
        self._count = [0] * size
        self._sum = [0] * size
        self._a = [1] * size
        self._b = [0] * size
        self._lo = [-1] * size
        self._hi = [0] * size
        self._xs = []
        self._ys = []
        self._values = []
        self._order = [0] * n
        if not n:
            return
        x_order = sorted(range(n), key=lambda i: points[i][0])
        y_order = sorted(range(n), key=lambda i: points[i][1])
        tasks = [(1, x_order, y_order, 0)]
        marks = [0] * n
        generation = 0
        order = []
        while tasks:
            node, x_order, y_order, axis = tasks.pop()
            indices = x_order if axis == 0 else y_order
            order.append(node)
            if len(indices) <= _BUCKET_SIZE:
                self._lo[node] = len(self._xs)
                for i in indices:
                    x, y, value = points[i]
                    self._position[i] = node
                    self._order[i] = len(self._xs)
                    self._xs.append(x)
                    self._ys.append(y)
                    self._values.append(-1 if value is None else value % mod)
                    if value is not None:
                        self._count[node] += 1
                        self._sum[node] += value
                self._sum[node] %= mod
                self._hi[node] = len(self._xs)
                self._xmin[node] = min(points[i][0] for i in indices)
                self._xmax[node] = max(points[i][0] for i in indices)
                self._ymin[node] = min(points[i][1] for i in indices)
                self._ymax[node] = max(points[i][1] for i in indices)
            else:
                if _ADAPTIVE_AXES:
                    nx = len({points[i][0] for i in x_order})
                    ny = len({points[i][1] for i in y_order})
                    if nx == 1 or ny > 1 and ny * 4 < nx:
                        axis = 1
                    elif ny == 1 or nx > 1 and nx * 4 < ny:
                        axis = 0
                    indices = x_order if axis == 0 else y_order
                middle = len(indices) >> 1
                first, second = indices[:middle], indices[middle:]
                generation += 1
                for i in first:
                    marks[i] = generation
                other = y_order if axis == 0 else x_order
                low = [i for i in other if marks[i] == generation]
                high = [i for i in other if marks[i] != generation]
                if axis == 0:
                    tasks.append((node * 2 + 1, second, high, 1))
                    tasks.append((node * 2, first, low, 1))
                else:
                    tasks.append((node * 2 + 1, high, second, 0))
                    tasks.append((node * 2, low, first, 0))
        for node in reversed(order):
            if self._lo[node] < 0:
                left, right = node * 2, node * 2 + 1
                self._xmin[node] = min(self._xmin[left], self._xmin[right])
                self._xmax[node] = max(self._xmax[left], self._xmax[right])
                self._ymin[node] = min(self._ymin[left], self._ymin[right])
                self._ymax[node] = max(self._ymax[left], self._ymax[right])
                self._count[node] = self._count[left] + self._count[right]
                self._sum[node] = (self._sum[left] + self._sum[right]) % mod

    def _apply(self, node, a, b):
        if not self._count[node]:
            return
        self._sum[node] = (a * self._sum[node] + b * self._count[node]) % self.mod
        self._a[node] = a * self._a[node] % self.mod
        self._b[node] = (a * self._b[node] + b) % self.mod

    def _push(self, node):
        a, b = self._a[node], self._b[node]
        if a != 1 or b:
            if self._lo[node] < 0:
                self._apply(node * 2, a, b)
                self._apply(node * 2 + 1, a, b)
            else:
                values = self._values
                mod = self.mod
                for i in range(self._lo[node], self._hi[node]):
                    if values[i] >= 0:
                        values[i] = (a * values[i] + b) % mod
            self._a[node], self._b[node] = 1, 0

    def _point(self, index):
        if not 0 <= index < self.n:
            raise IndexError("point index out of range")
        node = self._position[index]
        for shift in range(node.bit_length() - 1, 0, -1):
            self._push(node >> shift)
        return node

    def set(self, index, value):
        """入力順のindex番目の点をvalueへ置換する。Noneなら無効化する。"""
        node = self._point(index)
        self._push(node)
        i = self._order[index]
        old = self._values[i]
        self._count[node] += (value is not None) - (old >= 0)
        value = -1 if value is None else value % self.mod
        self._values[i] = value
        self._sum[node] = (self._sum[node] - max(0, old) + max(0, value)) % self.mod
        node >>= 1
        while node:
            self._sum[node] = (self._sum[node * 2] + self._sum[node * 2 + 1]) % self.mod
            self._count[node] = self._count[node * 2] + self._count[node * 2 + 1]
            node >>= 1

    def get(self, index):
        """現在の重みを返す。無効な点はNoneを返す。"""
        node = self._point(index)
        value = self._values[self._order[index]]
        return None if value < 0 else (self._a[node] * value + self._b[node]) % self.mod

    def apply(self, left, right, down, up, a, b):
        """半開矩形[left, right)×[down, up)内の有効な重みをa*w+bへ変更する。"""
        if left > right or down > up:
            raise ValueError("invalid half-open rectangle")
        if left == right or down == up or not self.n:
            return
        a, b = a % self.mod, b % self.mod
        xmin, xmax, ymin, ymax = self._xmin, self._xmax, self._ymin, self._ymax
        values, count = self._sum, self._count
        mod = self.mod
        stack = [1]
        parents = []
        while stack:
            node = stack.pop()
            if count[node] and not (xmax[node] < left or right <= xmin[node] or ymax[node] < down or up <= ymin[node]):
                if left <= xmin[node] and xmax[node] < right and down <= ymin[node] and ymax[node] < up:
                    self._apply(node, a, b)
                elif self._lo[node] >= 0:
                    xs, ys, weights = self._xs, self._ys, self._values
                    old_a, old_b = self._a[node], self._b[node]
                    new_a, new_b = a * old_a % mod, (a * old_b + b) % mod
                    total = 0
                    for i in range(self._lo[node], self._hi[node]):
                        weight = weights[i]
                        if weight >= 0:
                            if left <= xs[i] < right and down <= ys[i] < up:
                                weight = (new_a * weight + new_b) % mod
                            elif old_a != 1 or old_b:
                                weight = (old_a * weight + old_b) % mod
                            weights[i] = weight
                            total += weight
                    values[node] = total % mod
                    self._a[node], self._b[node] = 1, 0
                else:
                    self._push(node)
                    parents.append(node)
                    stack.append(node * 2 + 1)
                    stack.append(node * 2)
        for node in reversed(parents):
            values[node] = (values[node * 2] + values[node * 2 + 1]) % mod

    def sum(self, left, right, down, up):
        """半開矩形[left, right)×[down, up)内の有効な重みの和を返す。"""
        if left > right or down > up:
            raise ValueError("invalid half-open rectangle")
        if left == right or down == up or not self.n:
            return 0
        xmin, xmax, ymin, ymax = self._xmin, self._xmax, self._ymin, self._ymax
        values, count = self._sum, self._count
        total = 0
        stack = [1]
        while stack:
            node = stack.pop()
            if count[node] and not (xmax[node] < left or right <= xmin[node] or ymax[node] < down or up <= ymin[node]):
                if left <= xmin[node] and xmax[node] < right and down <= ymin[node] and ymax[node] < up:
                    total += values[node]
                elif self._lo[node] >= 0:
                    xs, ys, weights = self._xs, self._ys, self._values
                    value = length = 0
                    for i in range(self._lo[node], self._hi[node]):
                        weight = weights[i]
                        if weight >= 0 and left <= xs[i] < right and down <= ys[i] < up:
                            value += weight
                            length += 1
                    total += (self._a[node] * value + self._b[node] * length) % self.mod
                else:
                    self._push(node)
                    stack.append(node * 2 + 1)
                    stack.append(node * 2)
        return total % self.mod

    def tolist(self):
        """入力順の現在の重みを新しいlistで返す。無効な点の要素はNone。"""
        if not self.n:
            return []
        stack = [1]
        while stack:
            node = stack.pop()
            self._push(node)
            if self._lo[node] < 0:
                stack.append(node * 2 + 1)
                stack.append(node * 2)
        return [None if self._values[i] < 0 else self._values[i] for i in self._order]

    def __str__(self):
        return str(self.tolist())

    def __repr__(self):
        if not self.n:
            return "RectangleAffineSum([], mod=%r)" % self.mod
        values = self.tolist()
        points = [(self._xs[j], self._ys[j], values[i]) for i, j in enumerate(self._order)]
        return "RectangleAffineSum(%r, mod=%r)" % (points, self.mod)
