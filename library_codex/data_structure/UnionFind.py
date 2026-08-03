"""要素の併合・連結判定・成分サイズを扱う基本Union-Find。"""

class UnionFind:
    __slots__ = ("n", "parent", "component_count")

    def __init__(self, size):
        self.n = size
        self.parent = [-1] * size
        self.component_count = size

    def find(self, node):
        parent = self.parent
        root = node
        while parent[root] >= 0:
            root = parent[root]
        while node != root:
            next_node = parent[node]
            parent[node] = root
            node = next_node
        return root

    leader = find
    root = find

    def merge(self, first, second):
        first = self.find(first)
        second = self.find(second)
        if first == second:
            return first
        parent = self.parent
        if parent[first] > parent[second]:
            first, second = second, first
        parent[first] += parent[second]
        parent[second] = first
        self.component_count -= 1
        return first

    unite = merge
    union = merge

    def same(self, first, second):
        return self.find(first) == self.find(second)

    def size(self, node):
        return -self.parent[self.find(node)]

    def groups(self):
        result = [[] for _ in range(self.n)]
        for node in range(self.n):
            result[self.find(node)].append(node)
        return [group for group in result if group]
