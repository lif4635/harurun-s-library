"""群の要素で表した頂点間の差を保ち、矛盾する制約を拒否する。"""


class PotentialUnionFind:
    __slots__ = ("n", "parent", "potential", "component_count", "op", "inv", "unit")

    def __init__(self, size, op, inv, unit):
        if size < 0:
            raise ValueError("size must be nonnegative")
        self.n = size
        self.parent = [-1] * size
        self.potential = [unit] * size
        self.component_count = size
        self.op = op
        self.inv = inv
        self.unit = unit

    def find(self, node):
        parent = self.parent
        if parent[node] < 0:
            return node
        path = []
        while parent[parent[node]] >= 0:
            path.append(node)
            node = parent[node]
        root = parent[node]
        potential = self.potential
        total = potential[node]
        op = self.op
        for vertex in reversed(path):
            total = op(total, potential[vertex])
            potential[vertex] = total
            parent[vertex] = root
        return root

    def weight(self, node):
        self.find(node)
        return self.potential[node]

    def merge(self, first, second, difference):
        root_first = self.find(first)
        root_second = self.find(second)
        potential = self.potential
        op = self.op
        target = op(potential[first], difference)
        if root_first == root_second:
            return target == potential[second]
        difference = op(target, self.inv(potential[second]))
        parent = self.parent
        if parent[root_first] > parent[root_second]:
            root_first, root_second = root_second, root_first
            difference = self.inv(difference)
        parent[root_first] += parent[root_second]
        parent[root_second] = root_first
        potential[root_second] = difference
        self.component_count -= 1
        return True

    def diff(self, first, second):
        if self.find(first) != self.find(second):
            return None
        return self.op(self.inv(self.potential[first]), self.potential[second])

    def same(self, first, second):
        return self.find(first) == self.find(second)

    def size(self, node):
        return -self.parent[self.find(node)]

    def tolist(self):
        return [(self.find(node), self.potential[node]) for node in range(self.n)]

    def __str__(self):
        return str(self.tolist())

    def __repr__(self):
        return "PotentialUnionFind(%r)" % self.tolist()
