"""区間を同じ値で上書きし、任意のモノイドの区間積を求める。"""


class RangeAssignSegTree:
    __slots__ = ("n", "size", "log", "data", "lazy", "op", "identity")

    def __init__(self, op, identity, values):
        if isinstance(values, int):
            if values < 0:
                raise ValueError("size must be nonnegative")
            values = [identity] * values
        else:
            values = list(values)
        n = len(values)
        size = 1 << (n - 1).bit_length() if n else 1
        data = [identity] * (size << 1)
        data[size:size + n] = values
        for node in range(size - 1, 0, -1):
            data[node] = op(data[node << 1], data[node << 1 | 1])
        self.n = n
        self.size = size
        self.log = size.bit_length() - 1
        self.data = data
        self.lazy = [None] * size
        self.op = op
        self.identity = identity

    def _push(self, node):
        tag = self.lazy[node]
        if tag is not None:
            child_tag = tag[1]
            child = node << 1
            self.data[child] = self.data[child | 1] = child_tag[0]
            if child < self.size:
                self.lazy[child] = self.lazy[child | 1] = child_tag
            self.lazy[node] = None

    def _prepare(self, left, right):
        for shift in range(self.log, 0, -1):
            if left >> shift << shift != left:
                self._push(left >> shift)
            if right >> shift << shift != right:
                self._push((right - 1) >> shift)

    def assign(self, left, right, value):
        if not 0 <= left <= right <= self.n:
            raise IndexError("invalid half-open range")
        if left == right:
            return
        left += self.size
        right += self.size
        self._prepare(left, right)
        first, last = left, right
        data, lazy, op, size = self.data, self.lazy, self.op, self.size
        tag = value, None
        while left < right:
            if left & 1:
                data[left] = tag[0]
                if left < size:
                    lazy[left] = tag
                left += 1
            if right & 1:
                right -= 1
                data[right] = tag[0]
                if right < size:
                    lazy[right] = tag
            left >>= 1
            right >>= 1
            if left < right:
                tag = op(tag[0], tag[0]), tag
        for shift in range(1, self.log + 1):
            if first >> shift << shift != first:
                node = first >> shift
                data[node] = op(data[node << 1], data[node << 1 | 1])
            if last >> shift << shift != last:
                node = (last - 1) >> shift
                data[node] = op(data[node << 1], data[node << 1 | 1])

    def prod(self, left, right):
        if not 0 <= left <= right <= self.n:
            raise IndexError("invalid half-open range")
        if left == right:
            return self.identity
        left += self.size
        right += self.size
        self._prepare(left, right)
        first = second = self.identity
        data, op = self.data, self.op
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

    def set(self, index, value):
        self.assign(index, index + 1, value)

    def add(self, index, value):
        self.set(index, self.op(value, self.get(index)))

    def get(self, index):
        if not 0 <= index < self.n:
            raise IndexError("index out of range")
        node = index + self.size
        for shift in range(self.log, 0, -1):
            self._push(node >> shift)
        return self.data[node]

    def all_prod(self):
        return self.data[1]

    def tolist(self):
        for node in range(1, self.size):
            self._push(node)
        return self.data[self.size:self.size + self.n]

    def __len__(self):
        return self.n

    def __str__(self):
        return str(self.tolist())

    def __repr__(self):
        return "RangeAssignSegTree(" + str(self.tolist()) + ")"
