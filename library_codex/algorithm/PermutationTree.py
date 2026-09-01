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


class PermutationTreeNode:
    """One strong common interval stored by ``PermutationTree``."""

    __slots__ = (
        "kind", "left", "right", "minimum", "maximum", "parent", "children"
    )

    def __init__(
        self, kind, left, right, minimum, maximum, parent=-1, children=None
    ):
        self.kind = kind
        self.left = left
        self.right = right
        self.minimum = minimum
        self.maximum = maximum
        self.parent = parent
        self.children = [] if children is None else children

    @property
    def size(self):
        """Number of permutation entries represented by this node."""
        return self.right - self.left

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


class PermutationTree:
    """Build the common-interval decomposition tree of a permutation."""

    LEAF = "leaf"
    LINEAR_ASC = "linear_asc"
    LINEAR_DESC = "linear_desc"
    PRIME = "prime"

    __slots__ = ("permutation", "nodes", "root")

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

        self.permutation = permutation
        self.nodes = nodes = []
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

            current = len(nodes)
            nodes.append(
                PermutationTreeNode(
                    self.LEAF, index, index + 1, value, value
                )
            )

            while True:
                kind = None
                if stack and nodes[stack[-1]].maximum + 1 == nodes[current].minimum:
                    kind = self.LINEAR_ASC
                if stack and nodes[current].maximum + 1 == nodes[stack[-1]].minimum:
                    kind = self.LINEAR_DESC

                if kind is not None:
                    previous = stack.pop()
                    if nodes[previous].kind == kind:
                        self._add_child(previous, current)
                        current = previous
                    else:
                        node = nodes[previous]
                        child = current
                        current = len(nodes)
                        nodes.append(
                            PermutationTreeNode(
                                kind,
                                node.left,
                                node.right,
                                node.minimum,
                                node.maximum,
                                children=[previous],
                            )
                        )
                        self._add_child(current, child)
                elif segment.prod(
                    0, index + 1 - (nodes[current].right - nodes[current].left)
                ) == 0:
                    first = nodes[current]
                    parent = len(nodes)
                    nodes.append(
                        PermutationTreeNode(
                            self.PRIME,
                            first.left,
                            first.right,
                            first.minimum,
                            first.maximum,
                            children=[current],
                        )
                    )
                    current = parent
                    while True:
                        self._add_child(current, stack.pop())
                        node = nodes[current]
                        if node.maximum - node.minimum + 1 == node.right - node.left:
                            break
                    nodes[current].children.reverse()
                else:
                    break
            stack.append(current)
            segment.add(0, index + 1, -1)

        if len(stack) != 1:
            raise RuntimeError("failed to construct a permutation tree")
        self.root = stack[0]
        for parent, node in enumerate(nodes):
            for child in node.children:
                nodes[child].parent = parent

    def _add_child(self, parent, child):
        nodes = self.nodes
        child_node = nodes[child]
        node = nodes[parent]
        node.children.append(child)
        if child_node.left < node.left:
            node.left = child_node.left
        if child_node.right > node.right:
            node.right = child_node.right
        if child_node.minimum < node.minimum:
            node.minimum = child_node.minimum
        if child_node.maximum > node.maximum:
            node.maximum = child_node.maximum

    def count_intervals(self):
        """Return the number of common index intervals represented by the tree."""
        result = 0
        for node in self.nodes:
            if node.kind == self.LINEAR_ASC or node.kind == self.LINEAR_DESC:
                count = len(node.children)
                result += count * (count - 1) // 2
            else:
                result += 1
        return result

    def intervals(self):
        """Return every common index interval as a half-open pair."""
        nodes = self.nodes
        result = [(node.left, node.right) for node in nodes]
        for node in nodes:
            if node.kind != self.LINEAR_ASC and node.kind != self.LINEAR_DESC:
                continue
            children = node.children
            last = len(children) - 1
            for first_index in range(len(children)):
                left = nodes[children[first_index]].left
                for last_index in range(first_index + 1, len(children)):
                    if first_index == 0 and last_index == last:
                        continue
                    result.append((left, nodes[children[last_index]].right))
        return result

    def tolist(self):
        """Return node fields in node-index order for debugging."""
        return [
            {
                "kind": node.kind,
                "left": node.left,
                "right": node.right,
                "minimum": node.minimum,
                "maximum": node.maximum,
                "parent": node.parent,
                "children": node.children[:],
            }
            for node in self.nodes
        ]

    def __str__(self):
        return str(self.tolist())

    def __repr__(self):
        return "PermutationTree(%r)" % self.tolist()
