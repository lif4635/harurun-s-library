"""辺追加される無向グラフの二部性を管理する。"""

class DynamicBipartiteGraph:
    """Add-only bipartiteness with parity Union-Find."""

    __slots__ = (
        "n", "parent", "parity", "count0", "count1", "bipartite",
        "maximum_side_sum"
    )

    def __init__(self, n):
        self.n = n
        self.parent = [-1] * n
        self.parity = [0] * n
        self.count0 = [1] * n
        self.count1 = [0] * n
        self.bipartite = True
        self.maximum_side_sum = n

    def find(self, vertex):
        root = vertex
        value = 0
        while self.parent[root] >= 0:
            value ^= self.parity[root]
            root = self.parent[root]
        while vertex != root:
            nxt = self.parent[vertex]
            edge = self.parity[vertex]
            self.parent[vertex] = root
            self.parity[vertex] = value
            value ^= edge
            vertex = nxt
        return root

    def color(self, vertex):
        self.find(vertex)
        return self.parity[vertex]

    def can_add_edge(self, first, second):
        if not self.bipartite:
            return False
        root_first = self.find(first)
        root_second = self.find(second)
        return (root_first != root_second
                or (self.parity[first] ^ self.parity[second]) == 1)

    can_unite = can_add_edge

    def add_edge(self, first, second):
        if not self.bipartite:
            return False
        root_first = self.find(first)
        root_second = self.find(second)
        first_color = self.parity[first]
        second_color = self.parity[second]
        if root_first == root_second:
            if first_color == second_color:
                self.bipartite = False
                self.maximum_side_sum = -1
                return False
            return True
        self.maximum_side_sum -= max(
            self.count0[root_first], self.count1[root_first]
        ) + max(self.count0[root_second], self.count1[root_second])
        relation = first_color ^ second_color ^ 1
        if self.parent[root_first] > self.parent[root_second]:
            root_first, root_second = root_second, root_first
        # Recompute orientation if union-by-size swapped the roots.
        self.parent[root_first] += self.parent[root_second]
        self.parent[root_second] = root_first
        self.parity[root_second] = relation
        if relation:
            self.count0[root_first] += self.count1[root_second]
            self.count1[root_first] += self.count0[root_second]
        else:
            self.count0[root_first] += self.count0[root_second]
            self.count1[root_first] += self.count1[root_second]
        self.maximum_side_sum += max(
            self.count0[root_first], self.count1[root_first]
        )
        return True

    unite = add_edge

    def is_bipartite(self):
        return self.bipartite

