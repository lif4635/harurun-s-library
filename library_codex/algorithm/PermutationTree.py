"""Common-interval decomposition tree of a permutation.

For a permutation ``p`` of ``range(n)``, an index interval ``[left, right)``
is common when its values form one consecutive integer interval.  The tree
stores all strong common intervals and compactly represents every common
interval.  Construction is iterative and takes O(N log N) time.

Node data is stored in flat arrays.  ``PermutationTreeNode`` objects are
lightweight read-only views created only when ``tree.nodes`` is accessed.
"""


class _RangeAddRangeMin:
    __slots__ = ("size", "log", "data", "lazy")

    def __init__(self, n):
        size = 1 << (n - 1).bit_length()
        self.size = size
        self.log = size.bit_length() - 1
        self.data = [0] * (size << 1)
        self.lazy = [0] * size

    def _push(self, node):
        value = self.lazy[node]
        if value:
            left = node << 1
            right = left | 1
            self.data[left] += value
            self.data[right] += value
            if left < self.size:
                self.lazy[left] += value
                self.lazy[right] += value
            self.lazy[node] = 0

    def add(self, left, right, value):
        if left == right:
            return
        size = self.size
        data = self.data
        lazy = self.lazy
        left += size
        right += size
        original_left = left
        original_right = right
        for shift in range(self.log, 0, -1):
            if (left >> shift) << shift != left:
                self._push(left >> shift)
            if (right >> shift) << shift != right:
                self._push((right - 1) >> shift)
        while left < right:
            if left & 1:
                data[left] += value
                if left < size:
                    lazy[left] += value
                left += 1
            if right & 1:
                right -= 1
                data[right] += value
                if right < size:
                    lazy[right] += value
            left >>= 1
            right >>= 1
        left = original_left
        right = original_right
        for shift in range(1, self.log + 1):
            if (left >> shift) << shift != left:
                node = left >> shift
                data[node] = min(data[node << 1], data[node << 1 | 1])
            if (right >> shift) << shift != right:
                node = (right - 1) >> shift
                data[node] = min(data[node << 1], data[node << 1 | 1])

    def prod(self, left, right):
        if left == right:
            return 10 ** 30
        data = self.data
        left += self.size
        right += self.size
        for shift in range(self.log, 0, -1):
            if (left >> shift) << shift != left:
                self._push(left >> shift)
            if (right >> shift) << shift != right:
                self._push((right - 1) >> shift)
        result = 10 ** 30
        while left < right:
            if left & 1:
                if data[left] < result:
                    result = data[left]
                left += 1
            if right & 1:
                right -= 1
                if data[right] < result:
                    result = data[right]
            left >>= 1
            right >>= 1
        return result


class PermutationTreeNode:
    """Read-only view of one strong common interval in a permutation tree."""

    __slots__ = ("_tree", "_index")

    def __init__(self, tree, index):
        if not isinstance(tree, PermutationTree):
            raise TypeError("tree must be a PermutationTree")
        count = len(tree._kind)
        if index < 0:
            index += count
        if index < 0 or index >= count:
            raise IndexError("node index out of range")
        self._tree = tree
        self._index = index

    @property
    def kind(self):
        return self._tree._KIND_NAMES[self._tree._kind[self._index]]

    @property
    def left(self):
        return self._tree._left[self._index]

    @property
    def right(self):
        return self._tree._right[self._index]

    @property
    def minimum(self):
        return self._tree._minimum[self._index]

    @property
    def maximum(self):
        return self._tree._maximum[self._index]

    @property
    def parent(self):
        return self._tree._parent[self._index]

    @property
    def children(self):
        start = self._tree._child_start[self._index]
        end = self._tree._child_start[self._index + 1]
        return self._tree._children[start:end]

    @property
    def size(self):
        """Number of permutation entries represented by this node."""
        return self._tree._right[self._index] - self._tree._left[self._index]

    def __repr__(self):
        return (
            "PermutationTreeNode(kind=%r, left=%r, right=%r, minimum=%r, "
            "maximum=%r, parent=%r, children=%r)"
            % (
                self.kind,
                self.left,
                self.right,
                self.minimum,
                self.maximum,
                self.parent,
                self.children,
            )
        )


class _PermutationTreeNodes:
    """Sequence that creates node views only when they are requested."""

    __slots__ = ("_tree",)

    def __init__(self, tree):
        self._tree = tree

    def __len__(self):
        return len(self._tree._kind)

    def __getitem__(self, index):
        if isinstance(index, slice):
            return [
                PermutationTreeNode(self._tree, i)
                for i in range(*index.indices(len(self)))
            ]
        return PermutationTreeNode(self._tree, index)

    def __iter__(self):
        tree = self._tree
        for index in range(len(tree._kind)):
            yield PermutationTreeNode(tree, index)


class PermutationTree:
    """Build the common-interval decomposition tree of a permutation."""

    LEAF = "leaf"
    LINEAR_ASC = "linear_asc"
    LINEAR_DESC = "linear_desc"
    PRIME = "prime"

    _LEAF = 0
    _LINEAR_ASC = 1
    _LINEAR_DESC = 2
    _PRIME = 3
    _KIND_NAMES = (LEAF, LINEAR_ASC, LINEAR_DESC, PRIME)

    __slots__ = (
        "permutation",
        "nodes",
        "root",
        "_kind",
        "_left",
        "_right",
        "_minimum",
        "_maximum",
        "_parent",
        "_child_start",
        "_children",
    )

    def __init__(self, permutation):
        permutation = list(permutation)
        n = len(permutation)
        if n == 0:
            raise ValueError("permutation must be nonempty")
        seen = bytearray(n)
        for value in permutation:
            if value < 0 or value >= n or seen[value]:
                raise ValueError("permutation must contain range(n) exactly once")
            seen[value] = 1

        kind = bytearray()
        left = []
        right = []
        minimum = []
        maximum = []
        parent = []
        child_lists = []

        def append_node(node_kind, node_left, node_right, node_min, node_max, children=None):
            node_index = len(kind)
            kind.append(node_kind)
            left.append(node_left)
            right.append(node_right)
            minimum.append(node_min)
            maximum.append(node_max)
            parent.append(-1)
            child_lists.append(children)
            if children is not None:
                for child in children:
                    parent[child] = node_index
            return node_index

        def add_child(node_index, child):
            node_children = child_lists[node_index]
            if node_children is None:
                node_children = []
                child_lists[node_index] = node_children
            node_children.append(child)
            parent[child] = node_index
            if left[child] < left[node_index]:
                left[node_index] = left[child]
            if right[child] > right[node_index]:
                right[node_index] = right[child]
            if minimum[child] < minimum[node_index]:
                minimum[node_index] = minimum[child]
            if maximum[child] > maximum[node_index]:
                maximum[node_index] = maximum[child]

        segment = _RangeAddRangeMin(n)
        high = [-1]
        low = [-1]
        stack = []

        for index, value in enumerate(permutation):
            while high[-1] >= 0 and value > permutation[high[-1]]:
                top = high[-1]
                segment.add(
                    high[-2] + 1, top + 1, value - permutation[top]
                )
                high.pop()
            high.append(index)
            while low[-1] >= 0 and value < permutation[low[-1]]:
                top = low[-1]
                segment.add(
                    low[-2] + 1, top + 1, permutation[top] - value
                )
                low.pop()
            low.append(index)

            current = append_node(
                self._LEAF, index, index + 1, value, value
            )

            while True:
                node_kind = -1
                if stack and maximum[stack[-1]] + 1 == minimum[current]:
                    node_kind = self._LINEAR_ASC
                if stack and maximum[current] + 1 == minimum[stack[-1]]:
                    node_kind = self._LINEAR_DESC

                if node_kind >= 0:
                    previous = stack.pop()
                    if kind[previous] == node_kind:
                        add_child(previous, current)
                        current = previous
                    else:
                        child = current
                        current = append_node(
                            node_kind,
                            left[previous],
                            right[previous],
                            minimum[previous],
                            maximum[previous],
                            [previous],
                        )
                        add_child(current, child)
                elif segment.prod(
                    0, index + 1 - (right[current] - left[current])
                ) == 0:
                    first = current
                    current = append_node(
                        self._PRIME,
                        left[first],
                        right[first],
                        minimum[first],
                        maximum[first],
                        [first],
                    )
                    while True:
                        add_child(current, stack.pop())
                        if maximum[current] - minimum[current] + 1 == right[current] - left[current]:
                            break
                    child_lists[current].reverse()
                else:
                    break
            stack.append(current)
            segment.add(0, index + 1, -1)

        if len(stack) != 1:
            raise RuntimeError("failed to construct a permutation tree")

        children = []
        child_start = [0]
        for node_children in child_lists:
            if node_children is not None:
                children.extend(node_children)
            child_start.append(len(children))

        self.permutation = permutation
        self.root = stack[0]
        self._kind = kind
        self._left = left
        self._right = right
        self._minimum = minimum
        self._maximum = maximum
        self._parent = parent
        self._child_start = child_start
        self._children = children
        self.nodes = _PermutationTreeNodes(self)

    def count_intervals(self):
        """Return the number of common index intervals represented by the tree."""
        kind = self._kind
        child_start = self._child_start
        result = 0
        for index, node_kind in enumerate(kind):
            if node_kind == self._LINEAR_ASC or node_kind == self._LINEAR_DESC:
                count = child_start[index + 1] - child_start[index]
                result += count * (count - 1) // 2
            else:
                result += 1
        return result

    def intervals(self):
        """Return every common index interval as a half-open pair."""
        kind = self._kind
        left = self._left
        right = self._right
        child_start = self._child_start
        children = self._children
        result = list(zip(left, right))
        for index, node_kind in enumerate(kind):
            if node_kind != self._LINEAR_ASC and node_kind != self._LINEAR_DESC:
                continue
            start = child_start[index]
            end = child_start[index + 1]
            last = end - 1
            for first_index in range(start, end):
                interval_left = left[children[first_index]]
                for last_index in range(first_index + 1, end):
                    if first_index == start and last_index == last:
                        continue
                    result.append((interval_left, right[children[last_index]]))
        return result

    def tolist(self):
        """Return node fields in node-index order for debugging."""
        names = self._KIND_NAMES
        starts = self._child_start
        children = self._children
        return [
            {
                "kind": names[self._kind[index]],
                "left": self._left[index],
                "right": self._right[index],
                "minimum": self._minimum[index],
                "maximum": self._maximum[index],
                "parent": self._parent[index],
                "children": children[starts[index]:starts[index + 1]],
            }
            for index in range(len(self._kind))
        ]

    def __str__(self):
        return str(self.tolist())

    def __repr__(self):
        return "PermutationTree(%r)" % self.tolist()
