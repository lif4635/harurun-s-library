"""Sparse point updates and range products on a huge integer domain.

Nodes are allocated only on paths that receive a value.  Use this instead of
an ordinary SegmentTree when the coordinate range is enormous but the number
of touched positions is small.
"""


class DynamicSegmentTree:
    __slots__ = (
        "left_bound", "right_bound", "left", "right", "data", "op", "identity"
    )

    def __init__(self, left, right, op, identity):
        if left >= right:
            raise ValueError("left must be smaller than right")
        self.left_bound = left
        self.right_bound = right
        self.left = [-1]
        self.right = [-1]
        self.data = [identity]
        self.op = op
        self.identity = identity

    def _new_node(self):
        node = len(self.data)
        self.left.append(-1)
        self.right.append(-1)
        self.data.append(self.identity)
        return node

    def _write(self, index, value, combine):
        if not self.left_bound <= index < self.right_bound:
            raise IndexError("index is out of range")
        node = 0
        left = self.left_bound
        right = self.right_bound
        path = []
        while right - left > 1:
            path.append(node)
            middle = (left + right) >> 1
            if index < middle:
                child = self.left[node]
                if child < 0:
                    child = self._new_node()
                    self.left[node] = child
                node = child
                right = middle
            else:
                child = self.right[node]
                if child < 0:
                    child = self._new_node()
                    self.right[node] = child
                node = child
                left = middle
        if combine:
            value = self.op(value, self.data[node])
        self.data[node] = value
        op = self.op
        identity = self.identity
        for node in reversed(path):
            left_node = self.left[node]
            right_node = self.right[node]
            self.data[node] = op(
                self.data[left_node] if left_node >= 0 else identity,
                self.data[right_node] if right_node >= 0 else identity,
            )

    def set(self, index, value):
        self._write(index, value, False)

    def get(self, index):
        if not self.left_bound <= index < self.right_bound:
            raise IndexError("index is out of range")
        node = 0
        left = self.left_bound
        right = self.right_bound
        while node >= 0 and right - left > 1:
            middle = (left + right) >> 1
            if index < middle:
                node = self.left[node]
                right = middle
            else:
                node = self.right[node]
                left = middle
        return self.data[node] if node >= 0 else self.identity

    def add(self, index, value):
        """indexの現在値をop(value, current)で置き換える。O(log W)。"""
        self._write(index, value, True)

    def prod(self, query_left, query_right):
        if query_left >= query_right:
            return self.identity
        result = self.identity
        op = self.op
        stack = [(0, self.left_bound, self.right_bound)]
        while stack:
            node, left, right = stack.pop()
            if node < 0 or query_right <= left or right <= query_left:
                continue
            if query_left <= left and right <= query_right:
                result = op(result, self.data[node])
                continue
            middle = (left + right) >> 1
            stack.append((self.right[node], middle, right))
            stack.append((self.left[node], left, middle))
        return result

    query = prod

    def all_prod(self):
        return self.data[0]

    def items(self):
        """identityでない設定済みleafを(index, value)の昇順listで返す。O(K)。"""
        result = []
        stack = [(0, self.left_bound, self.right_bound)]
        while stack:
            node, left, right = stack.pop()
            if node < 0:
                continue
            if right - left == 1:
                value = self.data[node]
                if value != self.identity:
                    result.append((left, value))
                continue
            middle = (left + right) >> 1
            stack.append((self.right[node], middle, right))
            stack.append((self.left[node], left, middle))
        return result

    def __str__(self):
        return str(dict(self.items()))

    def __repr__(self):
        return "DynamicSegmentTree(%r)" % dict(self.items())
