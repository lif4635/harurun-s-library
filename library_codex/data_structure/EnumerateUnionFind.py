"""各連結成分に含まれる要素を列挙できるUnion-Find。"""

from library_codex.data_structure.UnionFind import UnionFind

class EnumerateUnionFind(UnionFind):
    __slots__ = ("next",)

    def __init__(self, size):
        super().__init__(size)
        self.next = list(range(size))

    def merge(self, first, second):
        first_root = self.find(first)
        second_root = self.find(second)
        if first_root == second_root:
            return first_root
        self.next[first], self.next[second] = self.next[second], self.next[first]
        return super().merge(first_root, second_root)

    unite = merge

    def members(self, node):
        start = node
        result = [start]
        node = self.next[start]
        while node != start:
            result.append(node)
            node = self.next[node]
        return result
