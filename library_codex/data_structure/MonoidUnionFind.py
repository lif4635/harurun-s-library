"""連結成分ごとのmonoid集約値と辺数を保持するUnion-Find。"""

from library_codex.data_structure.UnionFind import UnionFind

class MonoidUnionFind(UnionFind):
    __slots__ = ("value", "op", "edge_count")

    def __init__(self, values, op):
        values = list(values)
        super().__init__(len(values))
        self.value = values
        self.op = op
        self.edge_count = [0] * len(values)

    def merge(self, first, second):
        first = self.find(first)
        second = self.find(second)
        if first == second:
            self.edge_count[first] += 1
            return first
        parent = self.parent
        if parent[first] > parent[second]:
            first, second = second, first
        parent[first] += parent[second]
        parent[second] = first
        self.value[first] = self.op(self.value[first], self.value[second])
        self.edge_count[first] += self.edge_count[second] + 1
        self.component_count -= 1
        return first

    unite = merge

    def get(self, node):
        return self.value[self.find(node)]

    def set(self, node, value):
        self.value[self.find(node)] = value

    def edges(self, node):
        return self.edge_count[self.find(node)]

    def has_cycle(self, node):
        root = self.find(node)
        return self.edge_count[root] >= -self.parent[root]
