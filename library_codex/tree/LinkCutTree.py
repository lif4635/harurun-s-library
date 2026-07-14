from operator import add, sub


class LinkCutTree:
    """Array based link-cut tree for path products and path actions.

    ``op`` may be non-commutative.  ``mapping(action, aggregate, length)``
    and ``composition(new, old)`` are only needed when ``path_apply`` is
    used.  composition means applying ``old`` first and then ``new``.
    """

    __slots__ = (
        "n",
        "left",
        "right",
        "parent",
        "size",
        "reverse",
        "value",
        "forward",
        "backward",
        "op",
        "identity",
        "mapping",
        "composition",
        "lazy",
        "has_lazy",
    )

    def __init__(
        self,
        values,
        op=add,
        identity=0,
        mapping=None,
        composition=None,
    ):
        if isinstance(values, int):
            if values < 0:
                raise ValueError("size must be nonnegative")
            values = [identity] * values
        else:
            values = list(values)
        n = len(values)
        self.n = n
        self.left = [-1] * n
        self.right = [-1] * n
        self.parent = [-1] * n
        self.size = [1] * n
        self.reverse = bytearray(n)
        self.value = values
        self.forward = values.copy()
        self.backward = values.copy()
        self.op = op
        self.identity = identity
        self.mapping = mapping
        self.composition = composition
        self.lazy = [None] * n
        self.has_lazy = bytearray(n)

    def _is_aux_root(self, node):
        parent = self.parent[node]
        return parent < 0 or (
            self.left[parent] != node and self.right[parent] != node
        )

    def _update(self, node):
        left = self.left[node]
        right = self.right[node]
        size = 1
        forward = self.value[node]
        backward = forward
        op = self.op
        if left >= 0:
            size += self.size[left]
            forward = op(self.forward[left], forward)
            backward = op(backward, self.backward[left])
        if right >= 0:
            size += self.size[right]
            forward = op(forward, self.forward[right])
            backward = op(self.backward[right], backward)
        self.size[node] = size
        self.forward[node] = forward
        self.backward[node] = backward

    def _toggle(self, node):
        self.left[node], self.right[node] = (
            self.right[node],
            self.left[node],
        )
        self.forward[node], self.backward[node] = (
            self.backward[node],
            self.forward[node],
        )
        self.reverse[node] ^= 1

    def _all_apply(self, node, action):
        mapping = self.mapping
        size = self.size[node]
        self.value[node] = mapping(action, self.value[node], 1)
        self.forward[node] = mapping(action, self.forward[node], size)
        self.backward[node] = mapping(action, self.backward[node], size)
        if self.has_lazy[node]:
            self.lazy[node] = self.composition(action, self.lazy[node])
        else:
            self.lazy[node] = action
            self.has_lazy[node] = 1

    def _push(self, node):
        left = self.left[node]
        right = self.right[node]
        if self.reverse[node]:
            if left >= 0:
                self._toggle(left)
            if right >= 0:
                self._toggle(right)
            self.reverse[node] = 0
        if self.has_lazy[node]:
            action = self.lazy[node]
            if left >= 0:
                self._all_apply(left, action)
            if right >= 0:
                self._all_apply(right, action)
            self.lazy[node] = None
            self.has_lazy[node] = 0

    def _rotate(self, node):
        parent = self.parent[node]
        grandparent = self.parent[parent]
        if self.left[parent] == node:
            middle = self.right[node]
            self.right[node] = parent
            self.left[parent] = middle
        else:
            middle = self.left[node]
            self.left[node] = parent
            self.right[parent] = middle
        if middle >= 0:
            self.parent[middle] = parent
        self.parent[parent] = node
        self.parent[node] = grandparent
        if grandparent >= 0:
            if self.left[grandparent] == parent:
                self.left[grandparent] = node
            elif self.right[grandparent] == parent:
                self.right[grandparent] = node
        self._update(parent)
        self._update(node)

    def _splay(self, node):
        stack = [node]
        current = node
        while not self._is_aux_root(current):
            current = self.parent[current]
            stack.append(current)
        while stack:
            self._push(stack.pop())
        while not self._is_aux_root(node):
            parent = self.parent[node]
            if not self._is_aux_root(parent):
                grandparent = self.parent[parent]
                if (self.left[grandparent] == parent) == (
                    self.left[parent] == node
                ):
                    self._rotate(parent)
                else:
                    self._rotate(node)
            self._rotate(node)
        return node

    def access(self, node):
        last = -1
        current = node
        parent = self.parent
        right = self.right
        while current >= 0:
            self._splay(current)
            right[current] = last
            self._update(current)
            last = current
            current = parent[current]
        self._splay(node)
        return last

    expose = access

    def make_root(self, node):
        self.access(node)
        self._toggle(node)

    evert = make_root

    def find_root(self, node):
        self.access(node)
        self._push(node)
        while self.left[node] >= 0:
            node = self.left[node]
            self._push(node)
        self._splay(node)
        return node

    get_root = find_root
    root = find_root

    def connected(self, first, second):
        if first == second:
            return True
        return self.find_root(first) == self.find_root(second)

    same = connected

    def link(self, child, parent):
        self.make_root(child)
        if self.find_root(parent) == child:
            return False
        self.parent[child] = parent
        return True

    def cut(self, first, second=None):
        if second is None:
            self.access(first)
            left = self.left[first]
            if left < 0:
                return False
            self._push(left)
            while self.right[left] >= 0:
                left = self.right[left]
                self._push(left)
            self._splay(left)
            self.parent[first] = -1
            self.right[left] = -1
            self._update(left)
            return True
        self.make_root(first)
        self.access(second)
        if self.left[second] != first or self.right[first] >= 0:
            return False
        self.left[second] = -1
        self.parent[first] = -1
        self._update(second)
        return True

    def lca(self, first, second, root=None):
        if root is not None:
            self.make_root(root)
        if not self.connected(first, second):
            return -1
        self.access(first)
        return self.access(second)

    def parent_of(self, node, root=None):
        if root is not None:
            self.make_root(root)
        self.access(node)
        parent = self.left[node]
        if parent < 0:
            return -1
        self._push(parent)
        while self.right[parent] >= 0:
            parent = self.right[parent]
            self._push(parent)
        self._splay(parent)
        return parent

    get_parent = parent_of

    def path_fold(self, first, second):
        self.make_root(first)
        self.access(second)
        return self.forward[second]

    fold = path_fold
    query = path_fold

    def path_apply(self, first, second, action):
        if self.mapping is None or self.composition is None:
            raise TypeError("mapping and composition are required")
        self.make_root(first)
        self.access(second)
        self._all_apply(second, action)

    apply = path_apply

    def path_length(self, first, second):
        self.make_root(first)
        self.access(second)
        return self.size[second]

    def kth_on_path(self, first, second, index):
        self.make_root(first)
        self.access(second)
        if index < 0 or index >= self.size[second]:
            return -1
        node = second
        while True:
            self._push(node)
            left = self.left[node]
            left_size = self.size[left] if left >= 0 else 0
            if index < left_size:
                node = left
            elif index == left_size:
                self._splay(node)
                return node
            else:
                index -= left_size + 1
                node = self.right[node]

    def get_kth(self, node, index):
        self.access(node)
        index = self.size[node] - 1 - index
        if index < 0:
            return -1
        current = node
        while True:
            self._push(current)
            left = self.left[current]
            left_size = self.size[left] if left >= 0 else 0
            if index < left_size:
                current = left
            elif index == left_size:
                self._splay(current)
                return current
            else:
                index -= left_size + 1
                current = self.right[current]

    def set_value(self, node, value):
        self.access(node)
        self.value[node] = value
        self._update(node)

    set_key = set_value
    set = set_value

    def get_value(self, node):
        self.access(node)
        return self.value[node]

    get_key = get_value
    get = get_value


class LazyLinkCutTree(LinkCutTree):
    __slots__ = ()

    def __init__(self, values, op, identity, mapping, composition):
        super().__init__(values, op, identity, mapping, composition)


class SubtreeLinkCutTree:
    """Link-cut tree for subtree products over a commutative group."""

    __slots__ = (
        "n",
        "left",
        "right",
        "parent",
        "reverse",
        "value",
        "total",
        "virtual",
        "op",
        "remove",
        "identity",
    )

    def __init__(self, values, op=add, remove=sub, identity=0):
        if isinstance(values, int):
            if values < 0:
                raise ValueError("size must be nonnegative")
            values = [identity] * values
        else:
            values = list(values)
        n = len(values)
        self.n = n
        self.left = [-1] * n
        self.right = [-1] * n
        self.parent = [-1] * n
        self.reverse = bytearray(n)
        self.value = values
        self.total = values.copy()
        self.virtual = [identity] * n
        self.op = op
        self.remove = remove
        self.identity = identity

    def _is_aux_root(self, node):
        parent = self.parent[node]
        return parent < 0 or (
            self.left[parent] != node and self.right[parent] != node
        )

    def _update(self, node):
        left = self.left[node]
        right = self.right[node]
        total = self.value[node]
        op = self.op
        if left >= 0:
            total = op(self.total[left], total)
        total = op(total, self.virtual[node])
        if right >= 0:
            total = op(total, self.total[right])
        self.total[node] = total

    def _toggle(self, node):
        self.left[node], self.right[node] = (
            self.right[node],
            self.left[node],
        )
        self.reverse[node] ^= 1

    def _push(self, node):
        if self.reverse[node]:
            left = self.left[node]
            right = self.right[node]
            if left >= 0:
                self._toggle(left)
            if right >= 0:
                self._toggle(right)
            self.reverse[node] = 0

    def _rotate(self, node):
        parent = self.parent[node]
        grandparent = self.parent[parent]
        if self.left[parent] == node:
            middle = self.right[node]
            self.right[node] = parent
            self.left[parent] = middle
        else:
            middle = self.left[node]
            self.left[node] = parent
            self.right[parent] = middle
        if middle >= 0:
            self.parent[middle] = parent
        self.parent[parent] = node
        self.parent[node] = grandparent
        if grandparent >= 0:
            if self.left[grandparent] == parent:
                self.left[grandparent] = node
            elif self.right[grandparent] == parent:
                self.right[grandparent] = node
        self._update(parent)
        self._update(node)

    def _splay(self, node):
        stack = [node]
        current = node
        while not self._is_aux_root(current):
            current = self.parent[current]
            stack.append(current)
        while stack:
            self._push(stack.pop())
        while not self._is_aux_root(node):
            parent = self.parent[node]
            if not self._is_aux_root(parent):
                grandparent = self.parent[parent]
                if (self.left[grandparent] == parent) == (
                    self.left[parent] == node
                ):
                    self._rotate(parent)
                else:
                    self._rotate(node)
            self._rotate(node)
        return node

    def access(self, node):
        last = -1
        current = node
        while current >= 0:
            self._splay(current)
            old = self.right[current]
            if old >= 0:
                self.virtual[current] = self.op(
                    self.virtual[current], self.total[old]
                )
            self.right[current] = last
            if last >= 0:
                self.virtual[current] = self.remove(
                    self.virtual[current], self.total[last]
                )
            self._update(current)
            last = current
            current = self.parent[current]
        self._splay(node)
        return last

    expose = access

    def make_root(self, node):
        self.access(node)
        self._toggle(node)

    evert = make_root

    def find_root(self, node):
        self.access(node)
        self._push(node)
        while self.left[node] >= 0:
            node = self.left[node]
            self._push(node)
        self._splay(node)
        return node

    get_root = find_root

    def connected(self, first, second):
        if first == second:
            return True
        return self.find_root(first) == self.find_root(second)

    same = connected

    def link(self, child, parent):
        self.make_root(child)
        if self.find_root(parent) == child:
            return False
        self.access(parent)
        self.parent[child] = parent
        self.virtual[parent] = self.op(
            self.virtual[parent], self.total[child]
        )
        self._update(parent)
        return True

    def cut(self, first, second):
        self.make_root(first)
        self.access(second)
        if self.left[second] != first or self.right[first] >= 0:
            return False
        self.left[second] = -1
        self.parent[first] = -1
        self._update(second)
        return True

    def set_value(self, node, value):
        self.access(node)
        self.value[node] = value
        self._update(node)

    set_key = set_value

    def get_value(self, node):
        self.access(node)
        return self.value[node]

    get_key = get_value

    def subtree_fold(self, node, root=None):
        if root is not None:
            self.make_root(root)
        self.access(node)
        return self.op(self.value[node], self.virtual[node])

    subtree = subtree_fold

    def component_fold(self, node):
        self.make_root(node)
        return self.subtree_fold(node)


class SubtreeAddLinkCutTree:
    """Numeric link-cut tree supporting rooted subtree add and sum."""

    __slots__ = (
        "n",
        "left",
        "right",
        "parent",
        "reverse",
        "value",
        "total",
        "lazy",
        "cancel",
        "virtual_sum",
        "count",
        "virtual_count",
    )

    def __init__(self, values):
        if isinstance(values, int):
            if values < 0:
                raise ValueError("size must be nonnegative")
            values = [0] * values
        else:
            values = list(values)
        n = len(values)
        self.n = n
        self.left = [-1] * n
        self.right = [-1] * n
        self.parent = [-1] * n
        self.reverse = bytearray(n)
        self.value = values
        self.total = values.copy()
        self.lazy = [0] * n
        self.cancel = [0] * n
        self.virtual_sum = [0] * n
        self.count = [1] * n
        self.virtual_count = [0] * n

    def _is_aux_root(self, node):
        parent = self.parent[node]
        return parent < 0 or (
            self.left[parent] != node and self.right[parent] != node
        )

    def _apply(self, node, delta):
        self.value[node] += delta
        self.total[node] += delta * self.count[node]
        self.lazy[node] += delta
        self.virtual_sum[node] += delta * self.virtual_count[node]

    def _fetch(self, node):
        parent = self.parent[node]
        if parent < 0:
            return
        delta = self.lazy[parent] - self.cancel[node]
        if delta:
            self._apply(node, delta)
        self.cancel[node] = self.lazy[parent]

    def _update(self, node):
        left = self.left[node]
        right = self.right[node]
        total = self.value[node] + self.virtual_sum[node]
        count = 1 + self.virtual_count[node]
        if left >= 0:
            total += self.total[left]
            count += self.count[left]
            self.cancel[left] = self.lazy[node]
        if right >= 0:
            total += self.total[right]
            count += self.count[right]
            self.cancel[right] = self.lazy[node]
        self.total[node] = total
        self.count[node] = count

    def _toggle(self, node):
        self.left[node], self.right[node] = (
            self.right[node],
            self.left[node],
        )
        self.reverse[node] ^= 1

    def _push_reverse(self, node):
        if self.reverse[node]:
            left = self.left[node]
            right = self.right[node]
            if left >= 0:
                self._toggle(left)
            if right >= 0:
                self._toggle(right)
            self.reverse[node] = 0

    def _push(self, node):
        self._push_reverse(node)
        left = self.left[node]
        right = self.right[node]
        if left >= 0:
            self._fetch(left)
        if right >= 0:
            self._fetch(right)

    def _rotate(self, node):
        parent = self.parent[node]
        grandparent = self.parent[parent]
        self._push(parent)
        self._push(node)
        old_cancel = self.cancel[parent]
        if self.left[parent] == node:
            middle = self.right[node]
            self.right[node] = parent
            self.left[parent] = middle
        else:
            middle = self.left[node]
            self.left[node] = parent
            self.right[parent] = middle
        if middle >= 0:
            self.parent[middle] = parent
        self.parent[parent] = node
        self.parent[node] = grandparent
        if grandparent >= 0:
            if self.left[grandparent] == parent:
                self.left[grandparent] = node
            elif self.right[grandparent] == parent:
                self.right[grandparent] = node
        self._update(parent)
        self._update(node)
        self.cancel[node] = old_cancel

    def _splay(self, node):
        stack = [node]
        current = node
        while not self._is_aux_root(current):
            current = self.parent[current]
            stack.append(current)
        while stack:
            current = stack.pop()
            self._fetch(current)
            self._push(current)
        while not self._is_aux_root(node):
            parent = self.parent[node]
            if not self._is_aux_root(parent):
                grandparent = self.parent[parent]
                if (self.left[grandparent] == parent) == (
                    self.left[parent] == node
                ):
                    self._rotate(parent)
                else:
                    self._rotate(node)
            self._rotate(node)
        return node

    def access(self, node):
        last = -1
        current = node
        while current >= 0:
            self._splay(current)
            self._push(current)
            old = self.right[current]
            if old >= 0:
                self.virtual_sum[current] += self.total[old]
                self.virtual_count[current] += self.count[old]
            if last >= 0:
                self._fetch(last)
                self.virtual_sum[current] -= self.total[last]
                self.virtual_count[current] -= self.count[last]
            self.right[current] = last
            last = current
            current = self.parent[current]
        self._splay(node)
        return last

    expose = access

    def make_root(self, node):
        self.access(node)
        self._toggle(node)
        self._push(node)

    evert = make_root

    def find_root(self, node):
        self.access(node)
        self._push(node)
        while self.left[node] >= 0:
            node = self.left[node]
            self._push(node)
        self._splay(node)
        return node

    get_root = find_root

    def connected(self, first, second):
        if first == second:
            return True
        return self.find_root(first) == self.find_root(second)

    same = connected

    def link(self, child, parent):
        self.make_root(child)
        if self.find_root(parent) == child:
            return False
        self.access(parent)
        self.parent[child] = parent
        self.right[parent] = child
        self._update(parent)
        return True

    def cut(self, first, second):
        self.make_root(first)
        self.access(second)
        if self.left[second] != first or self.right[first] >= 0:
            return False
        self.left[second] = -1
        self.parent[first] = -1
        self._update(second)
        return True

    def set_value(self, node, value):
        self.access(node)
        self.value[node] = value
        self._update(node)

    set_key = set_value

    def get_value(self, node):
        self.access(node)
        return self.value[node]

    get_key = get_value

    def subtree_add(self, node, delta, root=None):
        if root is not None:
            self.make_root(root)
        self.access(node)
        left = self.left[node]
        if left >= 0:
            self.left[node] = -1
            self._update(node)
        self._apply(node, delta)
        if left >= 0:
            self.left[node] = left
            self._update(node)

    def subtree_sum(self, node, root=None):
        if root is not None:
            self.make_root(root)
        self.access(node)
        return self.value[node] + self.virtual_sum[node]

    subtree_fold = subtree_sum

    def component_sum(self, node):
        self.make_root(node)
        return self.subtree_sum(node)
