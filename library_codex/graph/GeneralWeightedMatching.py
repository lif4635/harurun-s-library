from collections import deque


class GeneralWeightedMatching:
    """Maximum-weight matching in a general graph (primal-dual blossom)."""

    __slots__ = (
        "n", "m", "stamp", "graph", "mate", "root", "used", "flower",
        "belong", "dual", "state", "slack", "parent", "queue", "infinity",
    )

    def __init__(self, vertex_count, infinity=10 ** 30):
        self.n = vertex_count
        self.m = vertex_count
        self.stamp = 0
        capacity = vertex_count * 2 + 2
        self.graph = [[(i, j, 0) for j in range(capacity)]
                      for i in range(capacity)]
        self.mate = [0] * capacity
        self.root = [0] * capacity
        self.used = [0] * capacity
        self.flower = [[] for _ in range(capacity)]
        self.belong = [[0] * capacity for _ in range(capacity)]
        self.dual = [0] * capacity
        self.state = [0] * capacity
        self.slack = [0] * capacity
        self.parent = [0] * capacity
        self.queue = deque()
        self.infinity = infinity
        for vertex in range(vertex_count + 1):
            self.root[vertex] = vertex
            self.belong[vertex][vertex] = vertex
            if vertex:
                self.dual[vertex] = infinity

    def add_edge(self, first, second, weight):
        if not 0 <= first < self.n or not 0 <= second < self.n:
            raise IndexError("vertex out of range")
        if first == second:
            return
        first += 1
        second += 1
        weight *= 2
        if weight > self.graph[first][second][2]:
            self.graph[first][second] = (first, second, weight)
            self.graph[second][first] = (second, first, weight)

    def _distance(self, edge):
        return self.dual[edge[0]] + self.dual[edge[1]] - edge[2]

    def _update(self, first, second):
        previous = self.slack[second]
        if previous == 0 or self._distance(self.graph[first][second]) < self._distance(
            self.graph[previous][second]
        ):
            self.slack[second] = first

    def _recalculate(self, vertex):
        self.slack[vertex] = 0
        for source in range(1, self.n + 1):
            if (self.graph[source][vertex][2]
                    and self.root[source] != vertex
                    and self.state[self.root[source]] == 1):
                self._update(source, vertex)

    def _push(self, vertex):
        stack = [vertex]
        while stack:
            current = stack.pop()
            if current <= self.n:
                self.queue.append(current)
            else:
                stack.extend(reversed(self.flower[current]))

    def _set_root(self, vertex, root):
        stack = [vertex]
        while stack:
            current = stack.pop()
            self.root[current] = root
            if current > self.n:
                stack.extend(self.flower[current])

    def _find_even(self, blossom, vertex):
        position = self.flower[blossom].index(vertex)
        if position & 1:
            self.flower[blossom][1:] = reversed(self.flower[blossom][1:])
            position = len(self.flower[blossom]) - position
        return position

    def _match(self, first, second):
        stack = [(0, first, second)]
        while stack:
            kind, first, second = stack.pop()
            if kind:
                position = first
                blossom = second
                values = self.flower[blossom]
                self.flower[blossom] = values[position:] + values[:position]
                continue
            self.mate[first] = self.graph[first][second][1]
            if first <= self.n:
                continue
            inside = self.belong[first][self.graph[first][second][0]]
            position = self._find_even(first, inside)
            stack.append((1, position, first))
            stack.append((0, inside, second))
            for index in range(position - 1, -1, -1):
                stack.append((0, self.flower[first][index],
                              self.flower[first][index ^ 1]))

    def _link(self, first, second):
        while True:
            next_vertex = self.root[self.mate[first]]
            self._match(first, second)
            if next_vertex == 0:
                return
            second = next_vertex
            first = self.root[self.parent[next_vertex]]
            self._match(second, first)

    def _make_blossom(self, first, second, lca):
        blossom = self.n + 1
        while blossom <= self.m and self.root[blossom]:
            blossom += 1
        if blossom > self.m:
            self.m += 1
        self.flower[blossom] = []
        for vertex in range(1, self.m + 1):
            self.graph[blossom][vertex] = (blossom, vertex, 0)
            self.graph[vertex][blossom] = (vertex, blossom, 0)
        for vertex in range(1, self.n + 1):
            self.belong[blossom][vertex] = 0
        self.state[blossom] = 1
        self.dual[blossom] = 0
        self.mate[blossom] = self.mate[lca]
        while first != lca:
            self.flower[blossom].append(first)
            first = self.root[self.mate[first]]
            self._push(first)
            self.flower[blossom].append(first)
            first = self.root[self.parent[first]]
        self.flower[blossom].append(lca)
        self.flower[blossom].reverse()
        while second != lca:
            self.flower[blossom].append(second)
            second = self.root[self.mate[second]]
            self._push(second)
            self.flower[blossom].append(second)
            second = self.root[self.parent[second]]
        self._set_root(blossom, blossom)
        for component in self.flower[blossom]:
            for vertex in range(1, self.m + 1):
                if (self.graph[blossom][vertex][2] == 0
                        or self._distance(self.graph[component][vertex])
                        < self._distance(self.graph[blossom][vertex])):
                    self.graph[blossom][vertex] = self.graph[component][vertex]
                    self.graph[vertex][blossom] = self.graph[vertex][component]
            for vertex in range(1, self.n + 1):
                if self.belong[component][vertex]:
                    self.belong[blossom][vertex] = component
        self._recalculate(blossom)

    def _expand(self, blossom):
        for component in self.flower[blossom]:
            self._set_root(component, component)
        inside = self.belong[blossom][self.graph[blossom][self.parent[blossom]][0]]
        self.state[inside] = 2
        self.parent[inside] = self.parent[blossom]
        position = self._find_even(blossom, inside)
        for index in range(0, position, 2):
            outer = self.flower[blossom][index]
            inner = self.flower[blossom][index + 1]
            self.state[inner] = 1
            self.state[outer] = 2
            self.parent[outer] = self.graph[inner][outer][0]
            self.slack[inner] = self.slack[outer] = 0
            self._push(inner)
        for index in range(position + 1, len(self.flower[blossom])):
            component = self.flower[blossom][index]
            self.state[component] = 0
            self._recalculate(component)
        self.flower[blossom] = []
        self.root[blossom] = 0

    def _path(self, edge):
        first = self.root[edge[0]]
        second = self.root[edge[1]]
        if self.state[second] == 0:
            self.parent[second] = edge[0]
            self.state[second] = 2
            next_vertex = self.root[self.mate[second]]
            self.slack[second] = self.slack[next_vertex] = 0
            self.state[next_vertex] = 1
            self._push(next_vertex)
        elif self.state[second] == 1:
            self.stamp += 1
            first_base = first
            second_base = second
            while first_base:
                self.used[first_base] = self.stamp
                first_base = self.root[self.mate[first_base]]
                if first_base:
                    first_base = self.root[self.parent[first_base]]
            lca = 0
            while second_base:
                if self.used[second_base] == self.stamp:
                    lca = second_base
                    break
                second_base = self.root[self.mate[second_base]]
                if second_base:
                    second_base = self.root[self.parent[second_base]]
            if lca:
                self._make_blossom(first, second, lca)
            else:
                self._link(first, second)
                self._link(second, first)
                return True
        return False

    def _augment(self):
        capacity = len(self.root)
        self.state = [0] * capacity
        self.slack = [0] * capacity
        self.parent = [0] * capacity
        self.queue = deque()
        for vertex in range(1, self.m + 1):
            if self.root[vertex] == vertex and self.mate[vertex] == 0:
                self.state[vertex] = 1
                self._push(vertex)
        if not self.queue:
            return False
        while True:
            while self.queue:
                vertex = self.queue.popleft()
                for other in range(1, self.n + 1):
                    if (self.graph[vertex][other][2]
                            and self.root[other] != self.root[vertex]):
                        if self._distance(self.graph[vertex][other]) == 0:
                            if self._path(self.graph[vertex][other]):
                                return True
                        elif self.state[self.root[other]] != 2:
                            self._update(vertex, self.root[other])
            delta = self.infinity
            for vertex in range(self.n + 1, self.m + 1):
                if self.root[vertex] == vertex and self.state[vertex] == 2:
                    delta = min(delta, self.dual[vertex] // 2)
            for vertex in range(1, self.m + 1):
                if (self.root[vertex] == vertex and self.slack[vertex]
                        and self.state[vertex] != 2):
                    distance = self._distance(
                        self.graph[self.slack[vertex]][vertex]
                    )
                    delta = min(delta, distance if self.state[vertex] == 0
                                else distance // 2)
            for vertex in range(1, self.n + 1):
                if self.state[self.root[vertex]] == 1:
                    self.dual[vertex] -= delta
                    if self.dual[vertex] <= 0:
                        return False
                elif self.state[self.root[vertex]] == 2:
                    self.dual[vertex] += delta
            for vertex in range(self.n + 1, self.m + 1):
                if self.root[vertex] == vertex and self.state[vertex]:
                    self.dual[vertex] += delta * (2 if self.state[vertex] == 1 else -2)
            for vertex in range(1, self.m + 1):
                source = self.slack[vertex]
                if (self.root[vertex] == vertex and source
                        and self.root[source] != vertex
                        and self._distance(self.graph[source][vertex]) == 0):
                    if self._path(self.graph[source][vertex]):
                        return True
            for vertex in range(self.n + 1, self.m + 1):
                if (self.root[vertex] == vertex and self.state[vertex] == 2
                        and self.dual[vertex] == 0):
                    self._expand(vertex)

    def run(self):
        while self._augment():
            pass
        return [self.mate[vertex] - 1 if self.mate[vertex] else -1
                for vertex in range(1, self.n + 1)]


WeightedMatching = GeneralWeightedMatching
