"""Persistent sparse range actions and range products.

Every range update creates a new version while older roots remain queryable.
Only nodes on changed paths are copied, so this fits branching histories over
a large coordinate domain without copying the whole array.
"""


class PersistentLazySegmentTree:
    __slots__ = (
        "left_bound", "right_bound", "left", "right", "data", "lazy",
        "pending", "roots", "op", "identity", "mapping", "composition"
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
        self.roots = [0]
        self.op = op
        self.identity = identity
        self.mapping = mapping
        self.composition = composition

    def _clone(self, node):
        new_node = len(self.data)
        if node < 0:
            self.left.append(-1)
            self.right.append(-1)
            self.data.append(self.identity)
            self.lazy.append(None)
            self.pending.append(0)
        else:
            self.left.append(self.left[node])
            self.right.append(self.right[node])
            self.data.append(self.data[node])
            self.lazy.append(self.lazy[node])
            self.pending.append(self.pending[node])
        return new_node

    def _all_apply(self, node, action, length):
        self.data[node] = self.mapping(action, self.data[node], length)
        if self.pending[node]:
            self.lazy[node] = self.composition(action, self.lazy[node])
        else:
            self.lazy[node] = action
            self.pending[node] = 1

    def _push_cloned(self, node, left, right):
        middle = (left + right) >> 1
        left_node = self._clone(self.left[node])
        right_node = self._clone(self.right[node])
        self.left[node] = left_node
        self.right[node] = right_node
        action = self.lazy[node]
        self._all_apply(left_node, action, middle - left)
        self._all_apply(right_node, action, right - middle)
        self.lazy[node] = None
        self.pending[node] = 0

    def apply(self, query_left, query_right, action, version=-1):
        old_root = self.roots[version]
        new_root = self._clone(old_root)
        if query_left >= query_right:
            self.roots.append(new_root)
            return len(self.roots) - 1
        stack = [(new_root, self.left_bound, self.right_bound, 0)]
        while stack:
            node, left, right, state = stack.pop()
            if state:
                left_node = self.left[node]
                right_node = self.right[node]
                self.data[node] = self.op(
                    self.data[left_node] if left_node >= 0 else self.identity,
                    self.data[right_node] if right_node >= 0 else self.identity,
                )
                continue
            if query_right <= left or right <= query_left:
                continue
            if query_left <= left and right <= query_right:
                self._all_apply(node, action, right - left)
                continue
            if self.pending[node]:
                self._push_cloned(node, left, right)
            middle = (left + right) >> 1
            stack.append((node, left, right, 1))
            if query_left < middle and left < query_right:
                child = self._clone(self.left[node])
                self.left[node] = child
                stack.append((child, left, middle, 0))
            if query_left < right and middle < query_right:
                child = self._clone(self.right[node])
                self.right[node] = child
                stack.append((child, middle, right, 0))
        self.roots.append(new_root)
        return len(self.roots) - 1

    range_apply = apply

    def prod(self, query_left, query_right, version=-1):
        if query_left >= query_right:
            return self.identity
        root = self.roots[version]
        result = self.identity
        stack = [
            (root, self.left_bound, self.right_bound, False, None)
        ]
        while stack:
            node, left, right, has_carry, carry = stack.pop()
            if query_right <= left or right <= query_left:
                continue
            if query_left <= left and right <= query_right:
                value = self.data[node] if node >= 0 else self.identity
                if has_carry:
                    value = self.mapping(carry, value, right - left)
                result = self.op(result, value)
                continue
            next_has = has_carry
            next_carry = carry
            if node >= 0 and self.pending[node]:
                if has_carry:
                    next_carry = self.composition(carry, self.lazy[node])
                else:
                    next_carry = self.lazy[node]
                    next_has = True
            middle = (left + right) >> 1
            right_node = self.right[node] if node >= 0 else -1
            left_node = self.left[node] if node >= 0 else -1
            stack.append(
                (right_node, middle, right, next_has, next_carry)
            )
            stack.append(
                (left_node, left, middle, next_has, next_carry)
            )
        return result

    query = prod

    def get(self, index, version=-1):
        return self.prod(index, index + 1, version)
