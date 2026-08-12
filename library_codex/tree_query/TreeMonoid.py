"""Point updates and monoid products on tree paths and subtrees."""

from library_codex.segment_tree.SegTree import SegTree
from library_codex.tree.HeavyLightDecomposition import HeavyLightDecomposition


class TreeMonoid:
    """Store one value per vertex in heavy-light order.

    The operation may be noncommutative: ``path_prod(u, v)`` folds values in
    the actual order from ``u`` to ``v``.
    """

    __slots__ = ("n", "op", "identity", "hld", "forward", "backward")

    def __init__(self, tree, op, identity, values, root=0):
        values = list(values)
        if len(values) != len(tree):
            raise ValueError("values has wrong length")
        hld = HeavyLightDecomposition(tree, root)
        ordered = [None] * len(tree)
        for vertex, value in enumerate(values):
            ordered[hld.tin[vertex]] = value
        self.n = len(tree)
        self.op = op
        self.identity = identity
        self.hld = hld
        self.forward = SegTree(op, identity, ordered)
        self.backward = SegTree(op, identity, reversed(ordered))

    def set(self, vertex, value):
        index = self.hld.tin[vertex]
        self.forward.set(index, value)
        self.backward.set(self.n - 1 - index, value)

    def get(self, vertex):
        return self.forward.get(self.hld.tin[vertex])

    def path_prod(self, first, second, edge=False):
        result = self.identity
        n = self.n
        for left, right, reverse in self.hld.path_ordered(first, second, edge):
            if reverse:
                value = self.backward.prod(n - right, n - left)
            else:
                value = self.forward.prod(left, right)
            result = self.op(result, value)
        return result

    def subtree_prod(self, vertex, edge=False):
        left, right = self.hld.subtree(vertex, edge)
        return self.forward.prod(left, right)
