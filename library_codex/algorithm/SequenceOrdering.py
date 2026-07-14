from functools import cmp_to_key


class _VersionIterator:
    __slots__ = ("owner", "index")

    def __init__(self, owner, index):
        self.owner = owner
        self.index = index

    @property
    def rank(self):
        ranks = self.owner.sorted_positions
        if ranks is None:
            raise RuntimeError("proc() has not been called")
        return ranks[self.index]

    def get(self):
        return self.rank

    def __int__(self):
        return self.rank

    def __index__(self):
        return self.rank


class PointUpdateLexSort:
    """Coordinate-compress all arrays in a sequence of point assignments.

    Persistent segment-tree roots make equality and first-difference searches
    exact.  No rolling hash or recursive traversal is used.
    """

    __slots__ = (
        "initial", "positions", "values", "sorted_positions", "maximum_rank",
    )

    def __init__(self, values):
        if not values:
            raise ValueError("the initial sequence must be nonempty")
        self.initial = list(values)
        self.positions = []
        self.values = []
        self.sorted_positions = None
        self.maximum_rank = -1

    def mutate(self, position, value):
        if not 0 <= position < len(self.initial):
            raise IndexError("position out of range")
        self.positions.append(position)
        self.values.append(value)
        self.sorted_positions = None
        return _VersionIterator(self, len(self.positions))

    def count(self):
        return len(self.positions) + 1

    def last(self):
        return _VersionIterator(self, len(self.positions))

    def max_sorted_pos(self):
        if self.sorted_positions is None:
            raise RuntimeError("proc() has not been called")
        return self.maximum_rank

    maxSortedPos = max_sorted_pos

    def proc(self):
        source = self.initial + self.values
        order = sorted(range(len(source)), key=source.__getitem__)
        compressed = [0] * len(source)
        rank = -1
        previous = None
        for index in order:
            value = source[index]
            if rank < 0 or previous < value or value < previous:
                rank += 1
                previous = value
            compressed[index] = rank

        length = len(self.initial)
        size = 1
        while size < length:
            size <<= 1
        left_child = [0]
        right_child = [0]
        leaf_value = [-1]

        leaf_nodes = {}
        internal_nodes = {}

        def get_leaf(value):
            node = leaf_nodes.get(value)
            if node is None:
                node = len(leaf_value)
                left_child.append(0)
                right_child.append(0)
                leaf_value.append(value)
                leaf_nodes[value] = node
            return node

        def get_internal(left, right):
            key = left, right
            node = internal_nodes.get(key)
            if node is None:
                node = len(leaf_value)
                left_child.append(left)
                right_child.append(right)
                leaf_value.append(-1)
                internal_nodes[key] = node
            return node

        leaves = [0] * size
        for index in range(size):
            leaves[index] = get_leaf(
                compressed[index] if index < length else 0
            )
        level = leaves
        while len(level) > 1:
            next_level = []
            for index in range(0, len(level), 2):
                next_level.append(get_internal(level[index], level[index + 1]))
            level = next_level
        root = level[0]
        roots = [root]

        for update_index, position in enumerate(self.positions):
            node = root
            lower = 0
            upper = size
            path = []
            while upper - lower > 1:
                middle = (lower + upper) >> 1
                if position < middle:
                    path.append((node, 0))
                    node = left_child[node]
                    upper = middle
                else:
                    path.append((node, 1))
                    node = right_child[node]
                    lower = middle
            new_value = compressed[length + update_index]
            if leaf_value[node] != new_value:
                current = get_leaf(new_value)
                while path:
                    parent, direction = path.pop()
                    if direction == 0:
                        current = get_internal(current, right_child[parent])
                    else:
                        current = get_internal(left_child[parent], current)
                root = current
            roots.append(root)

        def compare(first_index, second_index):
            first = roots[first_index]
            second = roots[second_index]
            if first == second:
                return 0
            while leaf_value[first] < 0:
                first_left = left_child[first]
                second_left = left_child[second]
                if first_left != second_left:
                    first = first_left
                    second = second_left
                else:
                    first = right_child[first]
                    second = right_child[second]
            first_value = leaf_value[first]
            second_value = leaf_value[second]
            return -1 if first_value < second_value else 1

        version_order = sorted(range(len(roots)), key=cmp_to_key(compare))
        positions = [0] * len(roots)
        current_rank = 0
        positions[version_order[0]] = 0
        for index in range(1, len(version_order)):
            if compare(version_order[index - 1], version_order[index]):
                current_rank += 1
            positions[version_order[index]] = current_rank
        self.sorted_positions = positions
        self.maximum_rank = current_rank
        return positions


PointUpdateLexicographicSort = PointUpdateLexSort
