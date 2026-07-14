class IncrementalForest:
    """Forest under link-only updates, rerooting the smaller component."""

    __slots__ = ("adjacency", "dsu", "parent", "parent_edge", "depths", "up",
                 "children_list", "edge_count")

    def __init__(self, size=0):
        self.adjacency = [[] for _ in range(size)]
        self.dsu = [-1] * size
        self.parent = [-1] * size
        self.parent_edge = [-1] * size
        self.depths = [0] * size
        self.up = [[-1] * size]
        self.children_list = [set() for _ in range(size)]
        self.edge_count = 0
        self._ensure_levels()

    def _ensure_levels(self):
        size = len(self.dsu)
        needed = max(1, size.bit_length())
        while len(self.up) < needed:
            previous = self.up[-1]
            current = [-1] * size
            for vertex, middle in enumerate(previous):
                current[vertex] = previous[middle] if middle >= 0 else -1
            self.up.append(current)

    def add_node(self):
        vertex = len(self.dsu)
        self.adjacency.append([])
        self.dsu.append(-1)
        self.parent.append(-1)
        self.parent_edge.append(-1)
        self.depths.append(0)
        self.children_list.append(set())
        for row in self.up:
            row.append(-1)
        self._ensure_levels()
        return vertex

    addNode = add_node

    def find(self, vertex):
        root = vertex
        while self.dsu[root] >= 0:
            root = self.dsu[root]
        while vertex != root:
            next_vertex = self.dsu[vertex]
            self.dsu[vertex] = root
            vertex = next_vertex
        return root

    rootOf = find

    def add_edge(self, first, second):
        first_root = self.find(first)
        second_root = self.find(second)
        if first_root == second_root:
            return -1
        if -self.dsu[first_root] < -self.dsu[second_root]:
            first, second = second, first
            first_root, second_root = second_root, first_root
        edge = self.edge_count
        self.edge_count += 1
        self.adjacency[first].append((second, edge))
        self.adjacency[second].append((first, edge))
        affected = []
        stack = [(second, first, edge)]
        while stack:
            vertex, parent, parent_edge = stack.pop()
            affected.append((vertex, parent, parent_edge))
            for neighbor, neighbor_edge in self.adjacency[vertex]:
                if neighbor != parent and self.find(neighbor) == second_root:
                    stack.append((neighbor, vertex, neighbor_edge))
        for vertex, _, _ in affected:
            old_parent = self.parent[vertex]
            if old_parent >= 0:
                self.children_list[old_parent].discard(vertex)
            self.children_list[vertex].clear()
        for vertex, parent, parent_edge in affected:
            self.parent[vertex] = parent
            self.parent_edge[vertex] = parent_edge
            self.depths[vertex] = self.depths[parent] + 1
            self.children_list[parent].add(vertex)
            self.up[0][vertex] = parent
            for level in range(1, len(self.up)):
                middle = self.up[level - 1][vertex]
                self.up[level][vertex] = (
                    self.up[level - 1][middle] if middle >= 0 else -1
                )
        self.dsu[first_root] += self.dsu[second_root]
        self.dsu[second_root] = first_root
        return edge

    addEdge = add_edge

    def connected(self, first, second):
        return self.find(first) == self.find(second)

    areConnected = connected

    def component_size(self, vertex):
        return -self.dsu[self.find(vertex)]

    componentSize = component_size

    def parent_of(self, vertex):
        return self.parent[vertex]

    parentOf = parent_of

    def parent_edge_of(self, vertex):
        return self.parent_edge[vertex]

    parentEdgeOf = parent_edge_of

    def depth(self, vertex):
        return self.depths[vertex]

    def ancestor_at_depth(self, vertex, target_depth):
        if target_depth < 0 or target_depth > self.depths[vertex]:
            return -1
        difference = self.depths[vertex] - target_depth
        level = 0
        while difference:
            if difference & 1:
                vertex = self.up[level][vertex]
            difference >>= 1
            level += 1
        return vertex

    la = ancestor_at_depth

    def lca(self, first, second):
        if not self.connected(first, second):
            return -1
        if self.depths[first] < self.depths[second]:
            first, second = second, first
        first = self.ancestor_at_depth(first, self.depths[second])
        if first == second:
            return first
        for level in range(len(self.up) - 1, -1, -1):
            if self.up[level][first] != self.up[level][second]:
                first = self.up[level][first]
                second = self.up[level][second]
        return self.parent[first]

    def middle(self, first, second, third):
        if not self.connected(first, second) or not self.connected(second, third):
            return -1
        return self.lca(first, second) ^ self.lca(second, third) ^ self.lca(third, first)

    def distance(self, first, second):
        ancestor = self.lca(first, second)
        return -1 if ancestor < 0 else (
            self.depths[first] + self.depths[second] - 2 * self.depths[ancestor]
        )

    dist = distance

    def kth_on_path(self, first, second, distance):
        total = self.distance(first, second)
        if total < 0 or not 0 <= distance <= total:
            return -1
        ancestor = self.lca(first, second)
        upward = self.depths[first] - self.depths[ancestor]
        if distance <= upward:
            return self.ancestor_at_depth(first, self.depths[first] - distance)
        remaining = total - distance
        return self.ancestor_at_depth(second, self.depths[second] - remaining)

    def children(self, vertex):
        return iter(self.children_list[vertex])

    def num_vertices(self):
        return len(self.dsu)

    numVertices = num_vertices
