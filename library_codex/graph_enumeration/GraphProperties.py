"""Recognition and coloring algorithms for undirected graphs."""

from library_codex.graph_matching.BipartiteEdgeColoring import bipartite_edge_coloring as _edge_coloring


class ChordalGraphRecognizer:
    """Maximum-cardinality-search chordal graph recognizer."""

    def __init__(self, graph):
        self.n = len(graph)
        self.adjacency = [list(set(neighbors) - {v})
                          for v, neighbors in enumerate(graph)]
        self._mcs = None
        self._peo = None
        self._chordal = None
        self._violation = None
        self._cycle = None

    def mcs_order(self):
        if self._mcs is not None:
            return self._mcs[:]
        n = self.n
        score = [0] * n
        previous = list(range(-1, n - 1))
        following = list(range(1, n)) + [-1] if n else []
        buckets = [-1] * (max(map(len, self.adjacency), default=0) + 1)
        buckets[0] = 0 if n else -1
        maximum = 0
        order = []
        for _ in range(n):
            while maximum and buckets[maximum] < 0:
                maximum -= 1
            v = buckets[maximum]
            after = following[v]
            buckets[maximum] = after
            if after >= 0:
                previous[after] = -1
            score[v] = -1
            order.append(v)
            for to in self.adjacency[v]:
                old = score[to]
                if old >= 0:
                    before, after = previous[to], following[to]
                    if before < 0:
                        buckets[old] = after
                    else:
                        following[before] = after
                    if after >= 0:
                        previous[after] = before
                    old += 1
                    score[to] = old
                    after = buckets[old]
                    previous[to] = -1
                    following[to] = after
                    if after >= 0:
                        previous[after] = to
                    buckets[old] = to
                    if old > maximum:
                        maximum = old
        self._mcs = order
        return order[:]

    def is_chordal(self):
        if self._chordal is not None:
            return self._chordal
        peo = list(reversed(self.mcs_order()))
        position = [0] * self.n
        for i, v in enumerate(peo):
            position[v] = i
        children = [-1] * self.n
        following = [-1] * self.n
        for v in peo:
            best = self.n
            parent = -1
            for to in self.adjacency[v]:
                if position[v] < position[to] < best:
                    best = position[to]
                    parent = to
            if parent >= 0:
                following[v] = children[parent]
                children[parent] = v
        marked = [-1] * self.n
        first_bad = self.n
        violation = None
        for parent in range(self.n):
            if children[parent] < 0:
                continue
            for to in self.adjacency[parent]:
                marked[to] = parent
            v = children[parent]
            while v >= 0:
                if position[v] < first_bad:
                    for to in self.adjacency[v]:
                        if position[to] > position[v] and to != parent and marked[to] != parent:
                            violation = (v, parent, to)
                            first_bad = position[v]
                            break
                v = following[v]
        self._peo = peo
        self._violation = violation
        self._chordal = violation is None
        return self._chordal

    def perfect_elimination_order(self):
        return self._peo[:] if self.is_chordal() else []

    def induced_cycle(self):
        """Return a chordless cycle witness, or [] for a chordal graph."""
        if self._cycle is not None:
            return self._cycle[:]
        if self.is_chordal():
            self._cycle = []
            return []
        v, source, target = self._violation
        position = [0] * self.n
        for i, vertex in enumerate(self._peo):
            position[vertex] = i
        forbidden = set(self.adjacency[v]) - {source, target}
        parent = [-1] * self.n
        parent[source] = source
        queue = [source]
        i = 0
        while i < len(queue):
            x = queue[i]
            i += 1
            if x == target:
                break
            for to in self.adjacency[x]:
                if (parent[to] == -1 and to != v and to not in forbidden
                        and position[to] > position[v]):
                    parent[to] = x
                    queue.append(to)
        if parent[target] == -1:
            # This should not occur for the MCS violation theorem, but keep the
            # recognizer result useful even if given asymmetric adjacency.
            self._cycle = []
            return []
        path = []
        x = target
        while x != source:
            path.append(x)
            x = parent[x]
        path.append(source)
        path.reverse()
        self._cycle = [v] + path
        return self._cycle[:]

def bipartite_edge_coloring(left_size, right_size, edges):
    """(最小色数, 入力辺と同じ順の色番号list)を返す。"""
    colors = _edge_coloring(left_size, right_size, edges)
    return max(colors, default=-1) + 1, colors
