"""木または森の2頂点に対するLCAと距離を取得する。"""

from library_codex.tree.EulerTour import EulerTour


class LCA:
    """Euler tourとRMQでLCAをO(1)で返す。"""

    __slots__ = ("n", "parent", "depth", "component", "_euler")

    def __init__(self, tree, root=0):
        euler = EulerTour(tree, root)
        self.n = euler.n
        self.parent = euler.parent
        self.depth = euler.depth
        self.component = euler.component
        self._euler = euler

    def __call__(self, first, second):
        """firstとsecondのLCAを返す。異なる連結成分なら-1。O(1)。"""
        return self._euler.lca(first, second)

    def dist(self, first, second):
        """firstとsecondの辺数距離を返す。異なる連結成分なら-1。O(1)。"""
        return self._euler.distance(first, second)
