from operator import add


class ImplicitTreap:
    __slots__ = (
        "root", "left", "right", "priority", "size", "reversed", "value",
        "forward", "backward", "lazy", "pending", "op", "identity",
        "mapping", "composition", "state"
    )

    def __init__(
        self,
        values=(),
        op=add,
        identity=0,
        mapping=None,
        composition=None,
    ):
        self.root = -1
        self.left = []
        self.right = []
        self.priority = []
        self.size = []
        self.reversed = bytearray()
        self.value = []
        self.forward = []
        self.backward = []
        self.lazy = []
        self.pending = bytearray()
        self.op = op
        self.identity = identity
        self.mapping = mapping
        self.composition = composition
        self.state = 0xD1B54A32D192ED03
        values = list(values)
        if values:
            stack = []
            for value in values:
                node = self._new(value)
                last = -1
                while stack and self.priority[node] < self.priority[stack[-1]]:
                    last = stack.pop()
                self.left[node] = last
                if stack:
                    self.right[stack[-1]] = node
                stack.append(node)
            self.root = stack[0]
            order = []
            stack = [self.root]
            while stack:
                node = stack.pop()
                order.append(node)
                if self.left[node] >= 0:
                    stack.append(self.left[node])
                if self.right[node] >= 0:
                    stack.append(self.right[node])
            for node in reversed(order):
                self._update(node)

    def _random(self):
        value = self.state
        value ^= value << 7 & ((1 << 64) - 1)
        value ^= value >> 9
        self.state = value
        return value

    def _new(self, value):
        node = len(self.value)
        self.left.append(-1)
        self.right.append(-1)
        self.priority.append(self._random())
        self.size.append(1)
        self.reversed.append(0)
        self.value.append(value)
        self.forward.append(value)
        self.backward.append(value)
        self.lazy.append(None)
        self.pending.append(0)
        return node

    def _update(self, node):
        left = self.left[node]
        right = self.right[node]
        value = self.value[node]
        forward = value
        backward = value
        size = 1
        op = self.op
        if left >= 0:
            forward = op(self.forward[left], forward)
            backward = op(backward, self.backward[left])
            size += self.size[left]
        if right >= 0:
            forward = op(forward, self.forward[right])
            backward = op(self.backward[right], backward)
            size += self.size[right]
        self.forward[node] = forward
        self.backward[node] = backward
        self.size[node] = size

    def _toggle(self, node):
        if node < 0:
            return
        self.left[node], self.right[node] = self.right[node], self.left[node]
        self.forward[node], self.backward[node] = self.backward[node], self.forward[node]
        self.reversed[node] ^= 1

    def _all_apply(self, node, action):
        mapping = self.mapping
        size = self.size[node]
        self.value[node] = mapping(action, self.value[node], 1)
        self.forward[node] = mapping(action, self.forward[node], size)
        self.backward[node] = mapping(action, self.backward[node], size)
        if self.pending[node]:
            self.lazy[node] = self.composition(action, self.lazy[node])
        else:
            self.lazy[node] = action
            self.pending[node] = 1

    def _push(self, node):
        left = self.left[node]
        right = self.right[node]
        if self.reversed[node]:
            self._toggle(left)
            self._toggle(right)
            self.reversed[node] = 0
        if self.pending[node]:
            action = self.lazy[node]
            if left >= 0:
                self._all_apply(left, action)
            if right >= 0:
                self._all_apply(right, action)
            self.lazy[node] = None
            self.pending[node] = 0

    def _split(self, root, count):
        left_path = []
        right_path = []
        node = root
        while node >= 0:
            self._push(node)
            left = self.left[node]
            left_size = self.size[left] if left >= 0 else 0
            if count <= left_size:
                right_path.append(node)
                node = left
            else:
                count -= left_size + 1
                left_path.append(node)
                node = self.right[node]
        first = -1
        for node in reversed(left_path):
            self.right[node] = first
            self._update(node)
            first = node
        second = -1
        for node in reversed(right_path):
            self.left[node] = second
            self._update(node)
            second = node
        return first, second

    def _merge(self, first, second):
        if first < 0:
            return second
        if second < 0:
            return first
        path = []
        while first >= 0 and second >= 0:
            if self.priority[first] < self.priority[second]:
                self._push(first)
                path.append((first, 1))
                first = self.right[first]
            else:
                self._push(second)
                path.append((second, 0))
                second = self.left[second]
        root = first if first >= 0 else second
        for node, direction in reversed(path):
            if direction:
                self.right[node] = root
            else:
                self.left[node] = root
            self._update(node)
            root = node
        return root

    def insert(self, index, value):
        first, second = self._split(self.root, index)
        self.root = self._merge(self._merge(first, self._new(value)), second)

    def append(self, value):
        self.insert(len(self), value)

    def appendleft(self, value):
        self.insert(0, value)

    def pop(self, index=-1):
        length = len(self)
        if index < 0:
            index += length
        if not 0 <= index < length:
            raise IndexError("pop index out of range")
        first, rest = self._split(self.root, index)
        middle, second = self._split(rest, 1)
        self._push(middle)
        value = self.value[middle]
        self.root = self._merge(first, second)
        return value

    def get(self, index):
        if index < 0:
            index += len(self)
        node = self.root
        while node >= 0:
            self._push(node)
            left = self.left[node]
            left_size = self.size[left] if left >= 0 else 0
            if index < left_size:
                node = left
            elif index == left_size:
                return self.value[node]
            else:
                index -= left_size + 1
                node = self.right[node]
        raise IndexError("index out of range")

    def set(self, index, value):
        if index < 0:
            index += len(self)
        node = self.root
        path = []
        while node >= 0:
            self._push(node)
            path.append(node)
            left = self.left[node]
            left_size = self.size[left] if left >= 0 else 0
            if index < left_size:
                node = left
            elif index == left_size:
                self.value[node] = value
                for current in reversed(path):
                    self._update(current)
                return
            else:
                index -= left_size + 1
                node = self.right[node]
        raise IndexError("index out of range")

    def reverse_range(self, left, right):
        first, rest = self._split(self.root, left)
        middle, second = self._split(rest, right - left)
        self._toggle(middle)
        self.root = self._merge(first, self._merge(middle, second))

    reverse = reverse_range

    def prod(self, left=0, right=None):
        if right is None:
            right = len(self)
        first, rest = self._split(self.root, left)
        middle, second = self._split(rest, right - left)
        value = self.forward[middle] if middle >= 0 else self.identity
        self.root = self._merge(first, self._merge(middle, second))
        return value

    query = prod

    def apply(self, left, right, action):
        if self.mapping is None or self.composition is None:
            raise TypeError("mapping and composition are required")
        first, rest = self._split(self.root, left)
        middle, second = self._split(rest, right - left)
        if middle >= 0:
            self._all_apply(middle, action)
        self.root = self._merge(first, self._merge(middle, second))

    range_apply = apply

    def to_list(self):
        result = []
        stack = []
        node = self.root
        while stack or node >= 0:
            while node >= 0:
                self._push(node)
                stack.append(node)
                node = self.left[node]
            node = stack.pop()
            result.append(self.value[node])
            node = self.right[node]
        return result

    def __getitem__(self, index):
        return self.get(index)

    def __setitem__(self, index, value):
        self.set(index, value)

    def __len__(self):
        return self.size[self.root] if self.root >= 0 else 0

    def __iter__(self):
        return iter(self.to_list())
