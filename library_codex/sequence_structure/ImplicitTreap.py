from operator import add


class ImplicitTreap:
    __slots__ = (
        "root", "left", "right", "priority", "size", "reversed", "value",
        "forward", "backward", "lazy", "pending", "op", "identity",
        "mapping", "composition", "state", "commutative"
    )

    def __init__(
        self,
        values=(),
        op=add,
        identity=0,
        mapping=None,
        composition=None,
        commutative=False,
    ):
        self.root = -1
        self.left = []
        self.right = []
        self.priority = []
        self.size = []
        self.reversed = bytearray()
        self.value = []
        self.forward = []
        self.backward = self.forward if commutative else []
        self.lazy = []
        self.pending = bytearray()
        self.op = op
        self.identity = identity
        self.mapping = mapping
        self.composition = composition
        self.commutative = commutative
        self.state = 0xD192ED03
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
        value ^= value << 13 & 0xFFFFFFFF
        value ^= value >> 17
        value ^= value << 5 & 0xFFFFFFFF
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
        if not self.commutative:
            self.backward.append(value)
        self.lazy.append(0)
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
            if not self.commutative:
                backward = op(backward, self.backward[left])
            size += self.size[left]
        if right >= 0:
            forward = op(forward, self.forward[right])
            if not self.commutative:
                backward = op(self.backward[right], backward)
            size += self.size[right]
        self.forward[node] = forward
        if not self.commutative:
            self.backward[node] = backward
        self.size[node] = size

    def _toggle(self, node):
        if node < 0:
            return
        self.left[node], self.right[node] = self.right[node], self.left[node]
        if not self.commutative:
            self.forward[node], self.backward[node] = self.backward[node], self.forward[node]
        self.reversed[node] ^= 1

    def _all_apply(self, node, action):
        mapping = self.mapping
        size = self.size[node]
        self.forward[node] = mapping(action, self.forward[node], size)
        if not self.commutative:
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
            self.value[node] = self.mapping(action, self.value[node], 1)
            if left >= 0:
                self._all_apply(left, action)
            if right >= 0:
                self._all_apply(right, action)
            self.lazy[node] = 0
            self.pending[node] = 0

    def _split(self, root, count, update=True):
        left = self.left
        right = self.right
        first = second = -1
        node = root
        while node >= 0:
            self._push(node)
            child = left[node]
            left_size = self.size[child] if child >= 0 else 0
            if count <= left_size:
                left[node] = second
                second, node = node, child
            else:
                count -= left_size + 1
                child = right[node]
                right[node] = first
                first, node = node, child
        root = -1
        while first >= 0:
            parent = right[first]
            right[first] = root
            if update:
                self._update(first)
            root, first = first, parent
        first = root
        root = -1
        while second >= 0:
            parent = left[second]
            left[second] = root
            if update:
                self._update(second)
            root, second = second, parent
        return first, root

    def _merge(self, first, second, push_first=False, push_second=False):
        left = self.left
        right = self.right
        priority = self.priority
        root = -1
        while first >= 0:
            if push_first:
                self._push(first)
            child = right[first]
            right[first] = root
            root, first = first, child
        first = root
        root = -1
        while second >= 0:
            if push_second:
                self._push(second)
            child = left[second]
            left[second] = root
            root, second = second, child
        second = root
        root = -1
        while first >= 0 or second >= 0:
            if second < 0 or first >= 0 and priority[first] > priority[second]:
                parent = right[first]
                right[first] = root
                self._update(first)
                root, first = first, parent
            else:
                parent = left[second]
                left[second] = root
                self._update(second)
                root, second = second, parent
        return root

    def insert(self, index, value):
        first, second = self._split(self.root, index, False)
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
        rest, second = self._split(self.root, index + 1, False)
        first, middle = self._split(rest, index, False)
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
        rest, second = self._split(self.root, right, False)
        first, middle = self._split(rest, left, False)
        self._toggle(middle)
        self.root = self._merge(self._merge(first, middle, False, True), second, True, False)

    reverse = reverse_range

    def prod(self, left=0, right=None):
        if right is None:
            right = len(self)
        if left >= right:
            return self.identity
        node = self.root
        op = self.op
        while node >= 0:
            if left == 0 and right == self.size[node]:
                return self.forward[node]
            self._push(node)
            first = self.left[node]
            second = self.right[node]
            count = self.size[first] if first >= 0 else 0
            if right <= count:
                node = first
            elif left > count:
                left -= count + 1
                right -= count + 1
                node = second
            else:
                break
        if node < 0:
            return self.identity
        center = self.value[node]
        prefix = self.identity
        right -= count + 1
        node = second
        while node >= 0 and right:
            if right == self.size[node]:
                prefix = op(prefix, self.forward[node])
                break
            self._push(node)
            child = self.left[node]
            count = self.size[child] if child >= 0 else 0
            if right <= count:
                node = child
            else:
                if child >= 0:
                    prefix = op(prefix, self.forward[child])
                prefix = op(prefix, self.value[node])
                right -= count + 1
                node = self.right[node]
        suffix = self.identity
        node = first
        while node >= 0 and left < self.size[node]:
            if left == 0:
                suffix = op(self.forward[node], suffix)
                break
            self._push(node)
            child = self.left[node]
            count = self.size[child] if child >= 0 else 0
            if left > count:
                left -= count + 1
                node = self.right[node]
            else:
                second = self.right[node]
                if second >= 0:
                    suffix = op(self.forward[second], suffix)
                suffix = op(self.value[node], suffix)
                node = child
        return op(op(suffix, center), prefix)

    query = prod

    def apply(self, left, right, action):
        if self.mapping is None or self.composition is None:
            raise TypeError("mapping and composition are required")
        rest, second = self._split(self.root, right, False)
        first, middle = self._split(rest, left, False)
        if middle >= 0:
            self._all_apply(middle, action)
        self.root = self._merge(self._merge(first, middle, False, True), second, True, False)

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

    def tolist(self):
        """遅延作用と反転を反映した現在の要素列を返す。O(N)。"""
        return self.to_list()

    def __str__(self):
        return str(self.to_list())

    def __repr__(self):
        return "ImplicitTreap(%r)" % self.to_list()

    def __getitem__(self, index):
        return self.get(index)

    def __setitem__(self, index, value):
        self.set(index, value)

    def __len__(self):
        return self.size[self.root] if self.root >= 0 else 0

    def __iter__(self):
        return iter(self.to_list())
