"""一般グラフの最大matchingを求める。"""

class GeneralMatching:
    """Edmonds blossom algorithm for maximum cardinality matching."""

    __slots__ = ("n", "graph", "mate", "matching_size")

    def __init__(self, graph):
        self.n = len(graph)
        self.graph = [list(dict.fromkeys(v for v in row if v != u))
                      for u, row in enumerate(graph)]
        self.mate = [-1] * self.n
        self.matching_size = 0
        self._solve()

    def _solve(self):
        n = self.n
        graph = self.graph
        mate = self.mate
        parent = [-1] * n
        base = list(range(n))
        used = [False] * n
        blossom = [False] * n

        def lca(first, second):
            path = [False] * n
            while True:
                first = base[first]
                path[first] = True
                if mate[first] == -1:
                    break
                first = parent[mate[first]]
            while True:
                second = base[second]
                if path[second]:
                    return second
                second = parent[mate[second]]

        def mark_path(vertex, common, child):
            while base[vertex] != common:
                blossom[base[vertex]] = True
                blossom[base[mate[vertex]]] = True
                parent[vertex] = child
                child = mate[vertex]
                vertex = parent[mate[vertex]]

        for root in range(n):
            if mate[root] != -1:
                continue
            for i in range(n):
                parent[i] = -1
                base[i] = i
                used[i] = False
            used[root] = True
            queue = [root]
            finish = -1
            head = 0
            while head < len(queue) and finish == -1:
                vertex = queue[head]
                head += 1
                for to in graph[vertex]:
                    if base[vertex] == base[to] or mate[vertex] == to:
                        continue
                    if to == root or (mate[to] != -1
                                      and parent[mate[to]] != -1):
                        common = lca(vertex, to)
                        for i in range(n):
                            blossom[i] = False
                        mark_path(vertex, common, to)
                        mark_path(to, common, vertex)
                        for i in range(n):
                            if blossom[base[i]]:
                                base[i] = common
                                if not used[i]:
                                    used[i] = True
                                    queue.append(i)
                    elif parent[to] == -1:
                        parent[to] = vertex
                        if mate[to] == -1:
                            finish = to
                            break
                        nxt = mate[to]
                        if not used[nxt]:
                            used[nxt] = True
                            queue.append(nxt)
            if finish == -1:
                continue
            self.matching_size += 1
            vertex = finish
            while vertex != -1:
                previous = parent[vertex]
                nxt = mate[previous] if previous != -1 else -1
                mate[vertex] = previous
                if previous != -1:
                    mate[previous] = vertex
                vertex = nxt

    def pairs(self):
        return [(v, to) for v, to in enumerate(self.mate) if v < to]

    maximum_matching = pairs

def maximum_general_matching(graph):
    solver = GeneralMatching(graph)
    return solver.matching_size, solver.mate

