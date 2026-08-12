"""木または森の2頂点に対するLCAと距離を取得する。"""

from library_codex.tree.EulerTour import EulerTour


class LCA:
    """Euler tourとRMQでLCAをO(1)で返す。"""

    __slots__ = ("n", "parent", "depth", "component", "_euler")

    def __init__(self, tree, root=0):
        """Euler tourとRMQを構築する。O(N)。"""
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

    def on_path(self, vertex, first, second):
        """Return whether ``vertex`` lies on the closed first--second path."""
        distance = self.dist(first, second)
        return (
            distance >= 0
            and self.dist(first, vertex) + self.dist(vertex, second) == distance
        )

    def path_intersection(self, first, second, third, fourth):
        """Return endpoints of two closed paths' intersection, or ``None``."""
        if (
            self.component[first] != self.component[second]
            or self.component[third] != self.component[fourth]
            or self.component[first] != self.component[third]
        ):
            return None
        vertices = [first, second, third, fourth]
        candidates = set(vertices)
        for i in range(4):
            for j in range(i):
                candidates.add(self(vertices[i], vertices[j]))
        common = [
            vertex for vertex in candidates
            if self.on_path(vertex, first, second)
            and self.on_path(vertex, third, fourth)
        ]
        if not common:
            return None
        endpoint_first = common[0]
        endpoint_second = common[0]
        best = 0
        for i, vertex in enumerate(common):
            for other in common[:i]:
                distance = self.dist(vertex, other)
                if distance > best:
                    best = distance
                    endpoint_first = vertex
                    endpoint_second = other
        return endpoint_first, endpoint_second
