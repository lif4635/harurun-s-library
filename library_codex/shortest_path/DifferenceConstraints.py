"""変数間の差の上下限から、整数解の復元と取り得る差の範囲を求める。"""

from heapq import heappop, heappush


class DifferenceConstraints:
    """差分制約を辺として保持し、実現可能な値と各変数の限界を求める。"""

    __slots__ = ("n", "_edges", "_potential", "_graph", "_reverse", "_solved")

    def __init__(self, n):
        if n < 0:
            raise ValueError("n must be nonnegative")
        self.n = n
        self._edges = []
        self._potential = self._graph = self._reverse = None
        self._solved = False

    def add(self, u, v, upper=None, *, lower=None):
        """lower <= x[v]-x[u] <= upperを追加する。Noneの側は制限しない。"""
        n = self.n
        if u is None:
            u = n
        if v is None:
            v = n
        if not 0 <= u <= n or not 0 <= v <= n:
            raise IndexError("vertex out of range")
        if upper is not None:
            self._edges.append((u, v, upper))
        if lower is not None:
            self._edges.append((v, u, -lower))
        self._solved = False
        self._potential = self._graph = self._reverse = None

    def fix(self, vertex, value):
        """1変数の値をvalueに固定する制約を追加する。"""
        if not 0 <= vertex < self.n:
            raise IndexError("vertex out of range")
        self.add(None, vertex, value, lower=value)

    def solve(self):
        """全制約を満たす整数値のlistを返す。矛盾する場合はNone。"""
        if not self._solved:
            n = self.n + 1
            distance = [0] * n
            edges = self._edges
            for _ in range(n):
                changed = False
                for u, v, weight in edges:
                    candidate = distance[u] + weight
                    if candidate < distance[v]:
                        distance[v] = candidate
                        changed = True
                if not changed:
                    break
            else:
                self._solved = True
                return None
            graph = [[] for _ in range(n)]
            reverse = [[] for _ in range(n)]
            for u, v, weight in edges:
                cost = weight + distance[u] - distance[v]
                graph[u].append((v, cost))
                reverse[v].append((u, cost))
            self._potential, self._graph, self._reverse = distance, graph, reverse
            self._solved = True
        if self._potential is None:
            return None
        origin = self._potential[self.n]
        return [value - origin for value in self._potential[:self.n]]

    def bounds(self, source=None):
        """全変数のx[v]-x[source]の最小値・最大値を返す。source=Noneは定数0。"""
        if source is None:
            source = self.n
        if not 0 <= source <= self.n:
            raise IndexError("source out of range")
        if not self._solved:
            self.solve()
        potential = self._potential
        if potential is None:
            raise ValueError("constraints are infeasible")
        upper = self._distances(self._graph, source)
        lower = self._distances(self._reverse, source)
        base = potential[source]
        return [(None if lower[v] is None else potential[v] - base - lower[v],
                 None if upper[v] is None else potential[v] - base + upper[v])
                for v in range(self.n)]

    @staticmethod
    def _distances(graph, source):
        distance = [None] * len(graph)
        distance[source] = 0
        queue = [(0, source)]
        while queue:
            cost, u = heappop(queue)
            if cost != distance[u]:
                continue
            for v, weight in graph[u]:
                candidate = cost + weight
                if distance[v] is None or candidate < distance[v]:
                    distance[v] = candidate
                    heappush(queue, (candidate, v))
        return distance

    def items(self):
        """各制約を(u, v, upper)で返す。None頂点は定数0を表す。"""
        n = self.n
        return [(None if u == n else u, None if v == n else v, w) for u, v, w in self._edges]

    def __repr__(self):
        return "DifferenceConstraints(n=" + str(self.n) + ", constraints=" + repr(self.items()) + ")"

    def __str__(self):
        return str(self.items())
