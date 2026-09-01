"""Common-interval decomposition tree of a permutation.

For a permutation ``p`` of ``range(n)``, an index interval ``[left, right)``
is common when its values form one consecutive integer interval.  The tree
stores all strong common intervals and compactly represents every common
interval.  Construction is iterative and takes O(N log N) time.
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


class PermutationTree:
    """Build the common-interval decomposition tree of a permutation."""

    LEAF = 0
    LINEAR_ASC = 1
    LINEAR_DESC = 2
    PRIME = 3
    _KIND_NAMES = ("leaf", "linear_asc", "linear_desc", "prime")

    __slots__ = (
        "permutation",
        "node_count",
        "root",
        "kind",
        "left",
        "right",
        "minimum",
        "maximum",
        "parent",
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
                self.LEAF, index, index + 1, value, value
            )

            while True:
                node_kind = -1
                if stack and maximum[stack[-1]] + 1 == minimum[current]:
                    node_kind = self.LINEAR_ASC
                if stack and maximum[current] + 1 == minimum[stack[-1]]:
                    node_kind = self.LINEAR_DESC

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
                        self.PRIME,
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
        self.node_count = len(kind)
        self.root = stack[0]
        self.kind = kind
        self.left = left
        self.right = right
        self.minimum = minimum
        self.maximum = maximum
        self.parent = parent
        self._child_start = child_start
        self._children = children

    def children(self, node):
        """Return child node indices from left to right."""
        start = self._child_start[node]
        end = self._child_start[node + 1]
        return self._children[start:end]

    def count_intervals(self):
        """Return the number of common index intervals represented by the tree."""
        kind = self.kind
        child_start = self._child_start
        result = 0
        for index, node_kind in enumerate(kind):
            if node_kind == self.LINEAR_ASC or node_kind == self.LINEAR_DESC:
                count = child_start[index + 1] - child_start[index]
                result += count * (count - 1) // 2
            else:
                result += 1
        return result

    def intervals(self):
        """Return every common index interval as a half-open pair."""
        kind = self.kind
        left = self.left
        right = self.right
        child_start = self._child_start
        children = self._children
        result = list(zip(left, right))
        for index, node_kind in enumerate(kind):
            if node_kind != self.LINEAR_ASC and node_kind != self.LINEAR_DESC:
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
                "kind": names[self.kind[index]],
                "left": self.left[index],
                "right": self.right[index],
                "minimum": self.minimum[index],
                "maximum": self.maximum[index],
                "parent": self.parent[index],
                "children": children[starts[index]:starts[index + 1]],
            }
            for index in range(self.node_count)
        ]

    def __str__(self):
        return str(self.tolist())

    def __repr__(self):
        return "PermutationTree(%r)" % self.tolist()
