class SegmentTree:
    __slots__ = ("n", "size", "log", "data", "op", "identity")

    def __init__(self, values, op, identity):
        if isinstance(values, int):
            n = values
            values = [identity] * n
        else:
            values = list(values)
            n = len(values)
        size = 1 << (n - 1).bit_length() if n else 1
        data = [identity] * (size << 1)
        data[size : size + n] = values
        for node in range(size - 1, 0, -1):
            data[node] = op(data[node << 1], data[node << 1 | 1])
        self.n = n
        self.size = size
        self.log = size.bit_length() - 1
        self.data = data
        self.op = op
        self.identity = identity

    def set(self, index, value):
        node = index + self.size
        data = self.data
        data[node] = value
        op = self.op
        node >>= 1
        while node:
            data[node] = op(data[node << 1], data[node << 1 | 1])
            node >>= 1

    def get(self, index):
        return self.data[index + self.size]

    def prod(self, left, right):
        left += self.size
        right += self.size
        first = self.identity
        second = self.identity
        data = self.data
        op = self.op
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

    def all_prod(self):
        return self.data[1]

    def max_right(self, left, predicate):
        if left == self.n:
            return self.n
        left += self.size
        value = self.identity
        data = self.data
        op = self.op
        while True:
            while not left & 1:
                left >>= 1
            merged = op(value, data[left])
            if not predicate(merged):
                while left < self.size:
                    left <<= 1
                    merged = op(value, data[left])
                    if predicate(merged):
                        value = merged
                        left += 1
                return min(left - self.size, self.n)
            value = merged
            left += 1
            if left & -left == left:
                break
        return self.n

    def min_left(self, right, predicate):
        if right == 0:
            return 0
        right += self.size
        value = self.identity
        data = self.data
        op = self.op
        while True:
            right -= 1
            while right > 1 and right & 1:
                right >>= 1
            merged = op(data[right], value)
            if not predicate(merged):
                while right < self.size:
                    right = right << 1 | 1
                    merged = op(data[right], value)
                    if predicate(merged):
                        value = merged
                        right -= 1
                return max(0, right + 1 - self.size)
            value = merged
            if right & -right == right:
                break
        return 0

    def __getitem__(self, index):
        return self.get(index)


class LazySegmentTree:
    __slots__ = (
        "n", "size", "log", "data", "lazy", "pending", "length",
        "op", "identity", "mapping", "composition"
    )

    def __init__(
        self,
        values,
        op,
        identity,
        mapping,
        composition,
    ):
        if isinstance(values, int):
            n = values
            values = [identity] * n
        else:
            values = list(values)
            n = len(values)
        size = 1 << (n - 1).bit_length() if n else 1
        data = [identity] * (size << 1)
        data[size : size + n] = values
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
        self.lazy = [None] * size
        self.pending = bytearray(size)
        self.length = length
        self.op = op
        self.identity = identity
        self.mapping = mapping
        self.composition = composition

    def _update(self, node):
        self.data[node] = self.op(
            self.data[node << 1], self.data[node << 1 | 1]
        )

    def _all_apply(self, node, action):
        self.data[node] = self.mapping(
            action, self.data[node], self.length[node]
        )
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
            self.lazy[node] = None
            self.pending[node] = 0

    def set(self, index, value):
        node = index + self.size
        for shift in range(self.log, 0, -1):
            self._push(node >> shift)
        self.data[node] = value
        for shift in range(1, self.log + 1):
            self._update(node >> shift)

    def get(self, index):
        node = index + self.size
        for shift in range(self.log, 0, -1):
            self._push(node >> shift)
        return self.data[node]

    def prod(self, left, right):
        if left == right:
            return self.identity
        left += self.size
        right += self.size
        for shift in range(self.log, 0, -1):
            if (left >> shift) << shift != left:
                self._push(left >> shift)
            if (right >> shift) << shift != right:
                self._push((right - 1) >> shift)
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
            if (left >> shift) << shift != left:
                self._push(left >> shift)
            if (right >> shift) << shift != right:
                self._push((right - 1) >> shift)
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
            if (left >> shift) << shift != left:
                self._update(left >> shift)
            if (right >> shift) << shift != right:
                self._update((right - 1) >> shift)

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
            self._push((node - 1) >> shift)
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


class DualSegmentTree:
    __slots__ = ("n", "size", "log", "value", "lazy", "pending", "mapping", "composition")

    def __init__(self, values, mapping, composition):
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
        self.lazy = [None] * size
        self.pending = bytearray(size)
        self.mapping = mapping
        self.composition = composition

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
        self.lazy[node] = None
        self.pending[node] = 0

    def apply(self, left, right, action):
        left += self.size
        right += self.size
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


class MaxInterval:
    __slots__ = (
        "sum", "maximum", "left_maximum", "right_maximum",
        "minimum", "left_minimum", "right_minimum", "length"
    )

    def __init__(self, value=0, length=0):
        self.length = length
        if length == 0:
            self.sum = 0
            self.maximum = 0
            self.left_maximum = 0
            self.right_maximum = 0
            self.minimum = 0
            self.left_minimum = 0
            self.right_minimum = 0
        else:
            total = value * length
            self.sum = total
            self.maximum = self.left_maximum = self.right_maximum = (
                total if value > 0 else value
            )
            self.minimum = self.left_minimum = self.right_minimum = (
                total if value < 0 else value
            )

    @classmethod
    def single(cls, value):
        return cls(value, 1)


def merge_max_interval(first, second):
    if first.length == 0:
        return second
    if second.length == 0:
        return first
    result = MaxInterval()
    result.length = first.length + second.length
    result.sum = first.sum + second.sum
    result.maximum = max(
        first.maximum,
        second.maximum,
        first.right_maximum + second.left_maximum,
    )
    result.left_maximum = max(
        first.left_maximum, first.sum + second.left_maximum
    )
    result.right_maximum = max(
        second.right_maximum, second.sum + first.right_maximum
    )
    result.minimum = min(
        first.minimum,
        second.minimum,
        first.right_minimum + second.left_minimum,
    )
    result.left_minimum = min(
        first.left_minimum, first.sum + second.left_minimum
    )
    result.right_minimum = min(
        second.right_minimum, second.sum + first.right_minimum
    )
    return result


def max_interval_segment_tree(values):
    return SegmentTree(
        [MaxInterval.single(value) for value in values],
        merge_max_interval,
        MaxInterval(),
    )
