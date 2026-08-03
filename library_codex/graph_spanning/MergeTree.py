class _UnionFind:
    __slots__ = ("parent",)

    def __init__(self, size):
        self.parent = [-1] * size

    def find(self, vertex):
        parent = self.parent
        root = vertex
        while parent[root] >= 0:
            root = parent[root]
        while vertex != root:
            next_vertex = parent[vertex]
            parent[vertex] = root
            vertex = next_vertex
        return root

    def unite(self, first, second):
        first = self.find(first)
        second = self.find(second)
        if first == second:
            return first
        if self.parent[first] > self.parent[second]:
            first, second = second, first
        self.parent[first] += self.parent[second]
        self.parent[second] = first
        return first


class MergeTree:
    """Pre-read union tree giving a contiguous leaf range for each live component."""

    __slots__ = ("n", "merges", "tree", "entry", "exit", "order", "position",
                 "union_find", "current", "processed")

    def __init__(self, vertex_count, merges):
        if vertex_count < 0:
            raise ValueError("vertex_count must be nonnegative")
        self.n = vertex_count
        self.merges = list(merges)
        size = vertex_count + len(self.merges) + 1
        root = size - 1
        tree = [[] for _ in range(size)]
        union_find = _UnionFind(vertex_count)
        current = list(range(vertex_count))
        for index, (first, second) in enumerate(self.merges):
            first_root = union_find.find(first)
            second_root = union_find.find(second)
            first_node = current[first_root]
            second_node = current[second_root]
            node = vertex_count + index
            tree[node].append(first_node)
            if second_node != first_node:
                tree[node].append(second_node)
            merged = union_find.unite(first_root, second_root)
            current[merged] = node
        seen = bytearray(vertex_count)
        for vertex in range(vertex_count):
            component = union_find.find(vertex)
            if not seen[component]:
                seen[component] = 1
                tree[root].append(current[component])
        entry = [-1] * size
        exit_ = [-1] * size
        order = []
        stack = [(root, 0)]
        while stack:
            node, phase = stack.pop()
            if phase == 0:
                entry[node] = len(order)
                if node < vertex_count:
                    order.append(node)
                    exit_[node] = len(order)
                else:
                    stack.append((node, 1))
                    for child in reversed(tree[node]):
                        stack.append((child, 0))
            else:
                exit_[node] = len(order)
        position = [0] * vertex_count
        for index, vertex in enumerate(order):
            position[vertex] = index
        self.tree = tree
        self.entry = entry
        self.exit = exit_
        self.order = order
        self.position = position
        self.union_find = _UnionFind(vertex_count)
        self.current = list(range(vertex_count))
        self.processed = 0

    def unite(self, first, second):
        if self.processed >= len(self.merges):
            raise IndexError("all pre-read merges were processed")
        expected = self.merges[self.processed]
        if {first, second} != {expected[0], expected[1]}:
            raise ValueError("unions must follow the pre-read order")
        root = self.union_find.unite(first, second)
        self.current[root] = self.n + self.processed
        self.processed += 1

    def component_node(self, vertex):
        return self.current[self.union_find.find(vertex)]

    get_id = component_node

    def component_range(self, vertex):
        node = self.component_node(vertex)
        return self.entry[node], self.exit[node]

    get_range = component_range

    def arrange(self, values):
        if len(values) != self.n:
            raise ValueError("wrong value count")
        return [values[vertex] for vertex in self.order]

    make_seq = arrange

    def restore(self, values):
        if len(values) != self.n:
            raise ValueError("wrong value count")
        result = [None] * self.n
        for index, vertex in enumerate(self.order):
            result[vertex] = values[index]
        return result

    restore_seq = restore

    def index(self, vertex):
        return self.position[vertex]
