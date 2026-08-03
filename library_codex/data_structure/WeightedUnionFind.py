"""要素間のpotential差を保ちながら併合する重み付きUnion-Find。"""

class WeightedUnionFind:
    __slots__ = ("n", "parent", "potential", "component_count")

    def __init__(self, size):
        self.n = size
        self.parent = [-1] * size
        self.potential = [0] * size
        self.component_count = size

    def find(self, node):
        parent = self.parent
        potential = self.potential
        root = node
        total = 0
        while parent[root] >= 0:
            total += potential[root]
            root = parent[root]
        prefix = 0
        while node != root:
            next_node = parent[node]
            weight = potential[node]
            parent[node] = root
            potential[node] = total - prefix
            prefix += weight
            node = next_node
        return root

    leader = find

    def weight(self, node):
        self.find(node)
        return self.potential[node]

    def merge(self, first, second, difference):
        difference += self.weight(first) - self.weight(second)
        first = self.find(first)
        second = self.find(second)
        if first == second:
            return difference == 0
        parent = self.parent
        if parent[first] > parent[second]:
            first, second = second, first
            difference = -difference
        parent[first] += parent[second]
        parent[second] = first
        self.potential[second] = difference
        self.component_count -= 1
        return True

    unite = merge

    def same(self, first, second):
        return self.find(first) == self.find(second)

    def diff(self, first, second):
        if self.find(first) != self.find(second):
            return None
        return self.weight(second) - self.weight(first)

    difference = diff

    def size(self, node):
        return -self.parent[self.find(node)]
