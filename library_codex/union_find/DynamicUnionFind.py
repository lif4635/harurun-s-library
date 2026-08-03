"""任意のhashableな要素を必要時に追加できる動的Union-Find。"""

class DynamicUnionFind:
    __slots__ = ("parent", "component_size", "component_count")

    def __init__(self):
        self.parent = {}
        self.component_size = {}
        self.component_count = 0

    def add(self, node):
        if node in self.parent:
            return False
        self.parent[node] = node
        self.component_size[node] = 1
        self.component_count += 1
        return True

    def find(self, node):
        parent = self.parent
        if node not in parent:
            parent[node] = node
            self.component_size[node] = 1
            self.component_count += 1
            return node
        root = node
        while parent[root] != root:
            root = parent[root]
        while node != root:
            next_node = parent[node]
            parent[node] = root
            node = next_node
        return root

    leader = find

    def merge(self, first, second):
        first = self.find(first)
        second = self.find(second)
        if first == second:
            return first
        parent = self.parent
        size = self.component_size
        if size[first] < size[second]:
            first, second = second, first
        parent[second] = first
        size[first] += size.pop(second)
        self.component_count -= 1
        return first

    unite = merge

    def same(self, first, second):
        return self.find(first) == self.find(second)

    def size(self, node):
        return self.component_size[self.find(node)]
