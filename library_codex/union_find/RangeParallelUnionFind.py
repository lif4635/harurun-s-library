"""2つの同じ長さの区間をまとめて対応位置ごとに併合するUnion-Find。"""

from library_codex.union_find.UnionFind import UnionFind

class RangeParallelUnionFind:
    __slots__ = ("n", "level")

    def __init__(self, size):
        self.n = size
        self.level = [UnionFind(size) for _ in range(max(1, size.bit_length()))]

    def merge(self, first, second, length=1, callback=None):
        if length <= 0:
            return
        if first < 0 or second < 0 or first + length > self.n or second + length > self.n:
            raise IndexError("range is out of bounds")
        if length == 1:
            stack = [(first, second, 0)]
        else:
            level = (length - 1).bit_length() - 1
            width = 1 << level
            stack = [
                (first, second, level),
                (first + length - width, second + length - width, level),
            ]
        while stack:
            left, right, level = stack.pop()
            union_find = self.level[level]
            left_root = union_find.find(left)
            right_root = union_find.find(right)
            if left_root == right_root:
                continue
            new_root = union_find.merge(left_root, right_root)
            if level == 0:
                if callback is not None:
                    old_root = right_root if new_root == left_root else left_root
                    callback(new_root, old_root)
                continue
            half = 1 << (level - 1)
            stack.append((left + half, right + half, level - 1))
            stack.append((left, right, level - 1))

    unite = merge

    def find(self, node):
        return self.level[0].find(node)

    def same(self, first, second):
        return self.level[0].same(first, second)

    def size(self, node):
        return self.level[0].size(node)
