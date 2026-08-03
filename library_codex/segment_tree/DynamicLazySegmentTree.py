"""Sparse range actions and range products on a huge integer domain.

Nodes are created only where an update or query descends.  Use this for a very
large coordinate interval when range updates and range aggregates are both
needed but most coordinates remain untouched.
"""


class DynamicLazySegmentTree:
    __slots__ = (
        "left_bound", "right_bound", "left", "right", "data", "lazy",
        "pending", "op", "identity", "mapping", "composition"
    )

    def __init__(self, left, right, op, identity, mapping, composition):
        if left >= right:
            raise ValueError("left must be smaller than right")
        self.left_bound = left
        self.right_bound = right
        self.left = [-1]
        self.right = [-1]
        self.data = [identity]
        self.lazy = [None]
        self.pending = bytearray(1)
        self.op = op
        self.identity = identity
        self.mapping = mapping
        self.composition = composition

    def _new_node(self):
        node = len(self.data)
        self.left.append(-1)
        self.right.append(-1)
        self.data.append(self.identity)
        self.lazy.append(None)
        self.pending.append(0)
        return node

    def _all_apply(self, node, action, length):
        self.data[node] = self.mapping(action, self.data[node], length)
        if self.pending[node]:
            self.lazy[node] = self.composition(action, self.lazy[node])
        else:
            self.lazy[node] = action
            self.pending[node] = 1

    def _push(self, node, left, right):
        middle = (left + right) >> 1
        left_node = self.left[node]
        if left_node < 0:
            left_node = self._new_node()
            self.left[node] = left_node
        right_node = self.right[node]
        if right_node < 0:
            right_node = self._new_node()
            self.right[node] = right_node
        if self.pending[node]:
            action = self.lazy[node]
            self._all_apply(left_node, action, middle - left)
            self._all_apply(right_node, action, right - middle)
            self.lazy[node] = None
            self.pending[node] = 0

    def apply(self, query_left, query_right, action):
        if query_left >= query_right:
            return
        stack = [(0, self.left_bound, self.right_bound, 0)]
        while stack:
            node, left, right, state = stack.pop()
            if state:
                left_node = self.left[node]
                right_node = self.right[node]
                self.data[node] = self.op(
                    self.data[left_node], self.data[right_node]
                )
                continue
            if query_right <= left or right <= query_left:
                continue
            if query_left <= left and right <= query_right:
                self._all_apply(node, action, right - left)
                continue
            self._push(node, left, right)
            middle = (left + right) >> 1
            stack.append((node, left, right, 1))
            stack.append((self.right[node], middle, right, 0))
            stack.append((self.left[node], left, middle, 0))

    range_apply = apply

    def prod(self, query_left, query_right):
        if query_left >= query_right:
            return self.identity
        result = self.identity
        stack = [(0, self.left_bound, self.right_bound)]
        while stack:
            node, left, right = stack.pop()
            if node < 0 or query_right <= left or right <= query_left:
                continue
            if query_left <= left and right <= query_right:
                result = self.op(result, self.data[node])
                continue
            self._push(node, left, right)
            middle = (left + right) >> 1
            stack.append((self.right[node], middle, right))
            stack.append((self.left[node], left, middle))
        return result

    query = prod

    def get(self, index):
        return self.prod(index, index + 1)

    def all_prod(self):
        return self.data[0]
