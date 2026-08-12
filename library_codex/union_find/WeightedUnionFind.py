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


class RollbackWeightedUnionFind:
    """Weighted Union-Find supporting snapshots and rollback.

    ``merge(a, b, d)`` adds the constraint ``weight(b)-weight(a)=d``.
    Path compression is intentionally omitted so every operation can be undone.
    """

    __slots__ = ("n", "parent", "potential", "history", "component_count")

    def __init__(self, size):
        self.n = size
        self.parent = [-1] * size
        self.potential = [0] * size
        self.history = []
        self.component_count = size

    def find(self, node):
        parent = self.parent
        total = 0
        while parent[node] >= 0:
            total += self.potential[node]
            node = parent[node]
        return node, total

    def leader(self, node):
        return self.find(node)[0]

    def weight(self, node):
        return self.find(node)[1]

    def merge(self, first, second, difference):
        root_first, weight_first = self.find(first)
        root_second, weight_second = self.find(second)
        difference += weight_first - weight_second
        if root_first == root_second:
            self.history.append(None)
            return difference == 0
        parent = self.parent
        if parent[root_first] > parent[root_second]:
            root_first, root_second = root_second, root_first
            difference = -difference
        self.history.append((root_first, root_second, parent[root_second]))
        parent[root_first] += parent[root_second]
        parent[root_second] = root_first
        self.potential[root_second] = difference
        self.component_count -= 1
        return True

    def same(self, first, second):
        return self.leader(first) == self.leader(second)

    def diff(self, first, second):
        root_first, weight_first = self.find(first)
        root_second, weight_second = self.find(second)
        if root_first != root_second:
            return None
        return weight_second - weight_first

    def size(self, node):
        return -self.parent[self.leader(node)]

    def snapshot(self):
        return len(self.history)

    def rollback(self, snapshot=None):
        if snapshot is None:
            snapshot = len(self.history) - 1
        if not 0 <= snapshot <= len(self.history):
            raise IndexError("invalid snapshot")
        while len(self.history) > snapshot:
            entry = self.history.pop()
            if entry is None:
                continue
            first, second, second_size = entry
            self.parent[first] -= second_size
            self.parent[second] = second_size
            self.potential[second] = 0
            self.component_count += 1
