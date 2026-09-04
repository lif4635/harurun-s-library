"""一般無向グラフの最大マッチングを求める。"""


class GeneralMatching:
    __slots__ = (
        "n", "graph", "mate", "matching_size", "_parent", "_seen",
        "_from", "_through",
    )

    def __init__(self, graph):
        self.n = len(graph)
        self.graph = [list(dict.fromkeys(v for v in row if v != u))
                      for u, row in enumerate(graph)]
        self.mate = [-1] * self.n
        self.matching_size = 0
        self._parent = [0] * self.n
        self._seen = [-1] * self.n
        self._from = [-1] * self.n
        self._through = [-1] * self.n
        for vertex in range(self.n):
            if self.mate[vertex] == -1:
                self.matching_size += self._augment(vertex)

    def _representative(self, vertex):
        seen = self._seen
        parent = self._parent
        stamp = self.matching_size
        path = []
        while seen[vertex] == stamp and parent[vertex] != -1:
            path.append(vertex)
            vertex = parent[vertex]
        for other in path:
            parent[other] = vertex
        return vertex

    def _restore(self, first, second):
        mate = self.mate
        edge_from = self._from
        edge_through = self._through
        stack = [(first, second)]
        while stack:
            first, second = stack.pop()
            previous = mate[first]
            mate[first] = second
            if previous == -1 or mate[previous] != first:
                continue
            edge_first = edge_from[first]
            edge_second = edge_through[first]
            if edge_second == -1:
                mate[previous] = edge_first
                stack.append((edge_first, previous))
            else:
                stack.append((edge_second, edge_first))
                stack.append((edge_first, edge_second))

    def _augment(self, root):
        graph = self.graph
        mate = self.mate
        parent = self._parent
        seen = self._seen
        edge_from = self._from
        edge_through = self._through
        stamp = self.matching_size
        queue = [root]
        head = 0
        seen[root] = stamp
        parent[root] = -1
        edge_from[root] = -1
        edge_through[root] = -1
        while head < len(queue):
            first = queue[head]
            head += 1
            for second in graph[first]:
                if second == root:
                    continue
                if mate[second] == -1:
                    mate[second] = first
                    self._restore(first, second)
                    return True
                if seen[second] == stamp:
                    x = self._representative(first)
                    y = self._representative(second)
                    if x == y:
                        continue
                    common = root
                    while x != root or y != root:
                        if y != root:
                            x, y = y, x
                        if edge_from[x] == first and edge_through[x] == second:
                            common = x
                            break
                        edge_from[x] = first
                        edge_through[x] = second
                        x = self._representative(edge_from[mate[x]])
                    for vertex in (
                        self._representative(first),
                        self._representative(second),
                    ):
                        while vertex != common:
                            seen[vertex] = stamp
                            parent[vertex] = common
                            queue.append(vertex)
                            vertex = self._representative(edge_from[mate[vertex]])
                    continue
                matched = mate[second]
                if seen[matched] == stamp:
                    continue
                edge_from[second] = -1
                edge_through[second] = -1
                seen[matched] = stamp
                parent[matched] = second
                edge_from[matched] = first
                edge_through[matched] = -1
                queue.append(matched)
        return False

    def pairs(self):
        return [(vertex, other) for vertex, other in enumerate(self.mate)
                if vertex < other]

    def essential_vertices(self):
        for vertex, other in enumerate(self.mate):
            if other == -1:
                self._augment(vertex)
        stamp = self.matching_size
        return [other != -1 and self._seen[vertex] != stamp
                for vertex, other in enumerate(self.mate)]
