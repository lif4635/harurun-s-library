"""Recognition and coloring algorithms for undirected graphs."""

from graph.BipartiteMatching import BipartiteMatching


class ChordalGraphRecognizer:
    """Maximum-cardinality-search chordal graph recognizer."""

    def __init__(self, graph):
        self.n = len(graph)
        self.adjacency = [set(neighbors) - {v}
                          for v, neighbors in enumerate(graph)]
        self._mcs = None
        self._peo = None
        self._chordal = None
        self._violation = None
        self._cycle = None

    def maximum_cardinality_search_order(self):
        if self._mcs is not None:
            return self._mcs[:]
        n = self.n
        score = [0] * n
        active = [True] * n
        buckets = [set() for _ in range(n + 1)]
        buckets[0].update(range(n))
        maximum = 0
        order = []
        for _ in range(n):
            while maximum and not buckets[maximum]:
                maximum -= 1
            v = buckets[maximum].pop()
            active[v] = False
            order.append(v)
            for to in self.adjacency[v]:
                if active[to]:
                    old = score[to]
                    buckets[old].remove(to)
                    old += 1
                    score[to] = old
                    buckets[old].add(to)
                    if old > maximum:
                        maximum = old
        self._mcs = order
        return order[:]

    def is_chordal(self):
        if self._chordal is not None:
            return self._chordal
        peo = list(reversed(self.maximum_cardinality_search_order()))
        position = [0] * self.n
        for i, v in enumerate(peo):
            position[v] = i
        violation = None
        for v in peo:
            later = [to for to in self.adjacency[v]
                     if position[to] > position[v]]
            if len(later) <= 1:
                continue
            parent = min(later, key=position.__getitem__)
            parent_neighbors = self.adjacency[parent]
            for to in later:
                if to != parent and to not in parent_neighbors:
                    violation = (v, parent, to)
                    break
            if violation is not None:
                break
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
        forbidden = self.adjacency[v] - {source, target}
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

    # Reference-style aliases.
    getMaximumCardinalitySearchOrder = maximum_cardinality_search_order
    isChordalGraph = is_chordal
    getPerfectEliminationOrdering = perfect_elimination_order
    findInducedCycle = induced_cycle


def bipartite_edge_coloring(left_size, right_size, edges):
    """Color a bipartite multigraph with exactly its maximum degree colors.

    Returns ``(number_of_colors, color_per_original_edge)``.  Repeated perfect
    matchings are extracted from a regularized graph; this favors compact,
    reliable PyPy code while preserving the optimal color count.
    """
    degree_left = [0] * left_size
    degree_right = [0] * right_size
    for left, right in edges:
        degree_left[left] += 1
        degree_right[right] += 1
    colors = max(max(degree_left, default=0), max(degree_right, default=0))
    if colors == 0:
        return 0, []
    size = max(left_size, right_size)
    regular_edges = list(edges)
    left_need = [colors - (degree_left[v] if v < left_size else 0)
                 for v in range(size)]
    right_need = [colors - (degree_right[v] if v < right_size else 0)
                  for v in range(size)]
    left = right = 0
    while left < size and right < size:
        while left < size and left_need[left] == 0:
            left += 1
        while right < size and right_need[right] == 0:
            right += 1
        if left == size or right == size:
            break
        amount = min(left_need[left], right_need[right])
        regular_edges.extend([(left, right)] * amount)
        left_need[left] -= amount
        right_need[right] -= amount

    active = [True] * len(regular_edges)
    answer = [-1] * len(edges)
    for color in range(colors):
        matching = BipartiteMatching(size, size)
        pair_edges = {}
        for edge_id, (left, right) in enumerate(regular_edges):
            if active[edge_id]:
                matching.add_edge(left, right)
                pair_edges.setdefault((left, right), []).append(edge_id)
        if matching.solve() != size:
            raise RuntimeError("regular bipartite graph lost a perfect matching")
        for left, right in matching.pairs():
            edge_id = pair_edges[left, right].pop()
            active[edge_id] = False
            if edge_id < len(edges):
                answer[edge_id] = color
    return colors, answer
