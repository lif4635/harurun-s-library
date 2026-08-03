"""隣接要素の連結区間と区間併合を管理するUnion-Find。"""

from library_codex.data_structure.UnionFind import UnionFind

class ContiguousUnionFind(UnionFind):
    __slots__ = ("left", "right")

    def __init__(self, size):
        super().__init__(size)
        self.left = list(range(size))
        self.right = [index + 1 for index in range(size)]

    def merge(self, first, second):
        first = self.find(first)
        second = self.find(second)
        if first == second:
            return first
        left = min(self.left[first], self.left[second])
        right = max(self.right[first], self.right[second])
        root = super().merge(first, second)
        self.left[root] = left
        self.right[root] = right
        return root

    unite = merge

    def range_merge(self, left, right):
        left = max(left, 0)
        right = min(right, self.n)
        if left >= right:
            return
        root = self.find(left)
        while self.right[root] < right:
            next_root = self.find(self.right[root])
            root = self.merge(root, next_root)

    range_unite = range_merge

    def interval(self, node):
        root = self.find(node)
        return self.left[root], self.right[root]
