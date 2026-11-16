"""過去版を残しながら両端操作・一点代入・分割・連結を行う列。"""


class PersistentDeque:
    __slots__ = ("_left", "_right", "_size", "_height", "_data", "_roots")

    def __init__(self, values=()):
        self._left, self._right = [0], [0]
        self._size, self._height, self._data = [0], [-1], [None]
        values = list(values)
        level = [self._leaf(tuple(values[i:i + 32])) for i in range(0, len(values), 32)]
        while len(level) > 1:
            level = [self._join(level[i], level[i + 1]) if i + 1 < len(level) else level[i] for i in range(0, len(level), 2)]
        self._roots = [level[0] if level else 0]

    def _leaf(self, values):
        if not values:
            return 0
        self._left.append(0)
        self._right.append(0)
        self._size.append(len(values))
        self._height.append(0)
        self._data.append(values)
        return len(self._size) - 1

    def _make(self, a, b):
        if not a or not b:
            return a or b
        if self._height[a] == self._height[b] == 0 and self._size[a] + self._size[b] <= 32:
            return self._leaf(self._data[a] + self._data[b])
        self._left.append(a)
        self._right.append(b)
        self._size.append(self._size[a] + self._size[b])
        self._height.append(max(self._height[a], self._height[b]) + 1)
        self._data.append(None)
        return len(self._size) - 1

    def _balance(self, a, b):
        height, left, right = self._height, self._left, self._right
        if height[a] > height[b] + 1:
            x, y = left[a], right[a]
            if height[x] >= height[y]:
                return self._make(x, self._make(y, b))
            return self._make(self._make(x, left[y]), self._make(right[y], b))
        if height[b] > height[a] + 1:
            x, y = left[b], right[b]
            if height[y] >= height[x]:
                return self._make(self._make(a, x), y)
            return self._make(self._make(a, left[x]), self._make(right[x], y))
        return self._make(a, b)

    def _join(self, a, b):
        if not a or not b:
            return a or b
        path = []
        while abs(self._height[a] - self._height[b]) > 1:
            if self._height[a] > self._height[b]:
                path.append((0, self._left[a]))
                a = self._right[a]
            else:
                path.append((1, self._right[b]))
                b = self._left[b]
        root = self._make(a, b)
        for side, fixed in reversed(path):
            root = self._balance(fixed, root) if side == 0 else self._balance(root, fixed)
        return root

    def _split(self, root, index):
        if index == 0:
            return 0, root
        if index == self._size[root]:
            return root, 0
        path = []
        while self._height[root] > 0:
            a, b = self._left[root], self._right[root]
            width = self._size[a]
            if index < width:
                path.append((0, b))
                root = a
            elif index > width:
                path.append((1, a))
                root = b
                index -= width
            else:
                break
        else:
            values = self._data[root]
            a, b = self._leaf(values[:index]), self._leaf(values[index:])
        for side, fixed in reversed(path):
            if side == 0:
                b = self._join(b, fixed)
            else:
                a = self._join(fixed, a)
        return a, b

    def _save(self, root):
        self._roots.append(root)
        return len(self._roots) - 1

    def size(self, version=-1):
        return self._size[self._roots[version]]

    def get(self, index, version=-1):
        root = self._roots[version]
        if not 0 <= index < self._size[root]:
            raise IndexError(index)
        while self._height[root] > 0:
            left = self._left[root]
            if index < self._size[left]:
                root = left
            else:
                index -= self._size[left]
                root = self._right[root]
        return self._data[root][index]

    def set(self, index, value, version=-1):
        root = self._roots[version]
        if not 0 <= index < self._size[root]:
            raise IndexError(index)
        path = []
        while self._height[root] > 0:
            a, b = self._left[root], self._right[root]
            if index < self._size[a]:
                path.append((0, b))
                root = a
            else:
                index -= self._size[a]
                path.append((1, a))
                root = b
        data = self._data[root]
        root = self._leaf(data[:index] + (value,) + data[index + 1:])
        for side, fixed in reversed(path):
            root = self._make(root, fixed) if side == 0 else self._make(fixed, root)
        return self._save(root)

    def split(self, index, version=-1):
        root = self._roots[version]
        if not 0 <= index <= self._size[root]:
            raise IndexError(index)
        a, b = self._split(root, index)
        return self._save(a), self._save(b)

    def concat(self, first, second):
        a, b = self._roots[first], self._roots[second]
        if self._size[a] + self._size[b] > 1 << 60:
            raise OverflowError("sequence is too long")
        return self._save(self._join(a, b))

    def push_front(self, value, version=-1):
        root = self._roots[version]
        if self._size[root] == 1 << 60:
            raise OverflowError("sequence is too long")
        return self._save(self._join(self._leaf((value,)), root))

    def push_back(self, value, version=-1):
        root = self._roots[version]
        if self._size[root] == 1 << 60:
            raise OverflowError("sequence is too long")
        return self._save(self._join(root, self._leaf((value,))))

    def pop_front(self, version=-1):
        root = self._roots[version]
        if not root:
            raise IndexError("empty deque")
        return self._save(self._split(root, 1)[1])

    def pop_back(self, version=-1):
        root = self._roots[version]
        if not root:
            raise IndexError("empty deque")
        return self._save(self._split(root, self._size[root] - 1)[0])

    def tolist(self, version=-1):
        root = self._roots[version]
        result, stack = [], [root] if root else []
        while stack:
            root = stack.pop()
            if self._height[root] == 0:
                result.extend(self._data[root])
            else:
                stack.extend((self._right[root], self._left[root]))
        return result

    def node_count(self):
        return len(self._size) - 1

    def __str__(self):
        return str(self.tolist())

    def __repr__(self):
        return "PersistentDeque(%r)" % self.tolist()
