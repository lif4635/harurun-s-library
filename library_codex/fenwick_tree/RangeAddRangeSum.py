"""区間加算と区間和を2本のFenwick Treeで処理する構造。"""

from library_codex.fenwick_tree.FenwickTree import FenwickTree

class RangeAddRangeSum:
    __slots__ = ("n", "first", "second")

    def __init__(self, values):
        if isinstance(values, int):
            n = values
            values = None
        else:
            values = list(values)
            n = len(values)
        self.n = n
        self.first = FenwickTree(n + 1)
        self.second = FenwickTree(n + 1)
        if values is not None:
            previous = 0
            for index, value in enumerate(values):
                delta = value - previous
                self.first.add(index, delta)
                self.second.add(index, delta * index)
                previous = value

    def add(self, left, right, value):
        if left >= right:
            return
        self.first.add(left, value)
        self.first.add(right, -value)
        self.second.add(left, value * left)
        self.second.add(right, -value * right)

    range_add = add

    def prefix_sum(self, right):
        return (
            self.first.prefix_sum(right) * right
            - self.second.prefix_sum(right)
        )

    def sum(self, left, right):
        return self.prefix_sum(right) - self.prefix_sum(left)

    prod = sum

    def get(self, index):
        return self.sum(index, index + 1)
