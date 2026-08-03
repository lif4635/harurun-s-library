"""Range actions with point queries.

Use this lighter structure when updates cover intervals but only individual
positions are queried.  It intentionally stores no range aggregate.
"""


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

    def tolist(self):
        """遅延作用を反映した現在の要素列をlistで返す。O(N)。"""
        for node in range(1, self.size):
            self._push(node)
        return self.value[:]

    def __str__(self):
        return str(self.tolist())

    def __repr__(self):
        return "DualSegmentTree(%r)" % self.tolist()
