"""二次元点への矩形更新と矩形集約を行うlazy KD-tree。"""

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
