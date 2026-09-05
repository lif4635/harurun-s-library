class PushRelabel:

    __slots__ = ("n", "graph", "to", "capacity", "position")

    def __init__(self, n):
        if n < 0:
            raise ValueError("number of vertices must be nonnegative")
        self.n = n
        self.graph = [[] for _ in range(n)]
        self.to = []
        self.capacity = []
        self.position = []

    def add_vertex(self):
        self.graph.append([])
        self.n += 1
        return self.n - 1

    def add_edge(self, source, target, capacity):
        if not (0 <= source < self.n and 0 <= target < self.n):
            raise IndexError("vertex out of range")
        if not isinstance(capacity, int):
            raise TypeError("capacity must be an integer")
        if capacity < 0:
            raise ValueError("capacity must be nonnegative")
        edge = len(self.to)
        self.graph[source].append(edge)
        self.to.append(target)
        self.capacity.append(capacity)
        self.graph[target].append(edge + 1)
        self.to.append(source)
        self.capacity.append(0)
        self.position.append((source, edge))
        return len(self.position) - 1

    def get_edge(self, index):
        source, edge = self.position[index]
        reverse_capacity = self.capacity[edge ^ 1]
        return (
            source,
            self.to[edge],
            self.capacity[edge] + reverse_capacity,
            reverse_capacity,
        )

    def edges(self):
        return [self.get_edge(i) for i in range(len(self.position))]

    def change_edge(self, index, capacity, flow):
        if not isinstance(capacity, int) or not isinstance(flow, int):
            raise TypeError("capacity and flow must be integers")
        if not (0 <= flow <= capacity):
            raise ValueError("flow must satisfy 0 <= flow <= capacity")
        _, edge = self.position[index]
        self.capacity[edge] = capacity - flow
        self.capacity[edge ^ 1] = flow

    def _global_relabel(self, source, sink, height, current):
        n = self.n
        unreachable = 2 * n
        height[:] = [unreachable] * n
        current[:] = [0] * n
        height[sink] = 0
        graph, to, residual = self.graph, self.to, self.capacity
        queue = [sink]
        for vertex in queue:
            next_height = height[vertex] + 1
            for edge in graph[vertex]:
                other = to[edge]
                if height[other] == unreachable and residual[edge ^ 1]:
                    height[other] = next_height
                    queue.append(other)
        height[source] = n
        queue = [source]
        for vertex in queue:
            next_height = height[vertex] + 1
            for edge in graph[vertex]:
                other = to[edge]
                if height[other] == unreachable and residual[edge ^ 1]:
                    height[other] = next_height
                    queue.append(other)

    def flow(self, source, sink, flow_limit=None):
        """Add and return flow up to ``flow_limit`` on the residual graph."""
        n = self.n
        if not (0 <= source < n and 0 <= sink < n):
            raise IndexError("vertex out of range")
        if source == sink:
            raise ValueError("source and sink must differ")
        if flow_limit is not None:
            if not isinstance(flow_limit, int):
                raise TypeError("flow limit must be an integer")
            if flow_limit < 0:
                raise ValueError("flow limit must be nonnegative")
        if flow_limit is None:
            return self._flow_unlimited(source, sink)
        if flow_limit == 0:
            return 0

        temporary_source = self.add_vertex()
        self.add_edge(temporary_source, source, flow_limit)
        try:
            return self._flow_unlimited(temporary_source, sink)
        finally:
            self.position.pop()
            self.graph[source].pop()
            self.graph.pop()
            self.to.pop()
            self.to.pop()
            self.capacity.pop()
            self.capacity.pop()
            self.n -= 1

    def _flow_unlimited(self, source, sink):
        n = self.n
        graph, to, residual = self.graph, self.to, self.capacity
        excess = [0] * n
        height = [0] * n
        current = [0] * n
        for edge in graph[source]:
            other = to[edge]
            if other == source:
                continue
            amount = residual[edge]
            if amount:
                residual[edge] = 0
                residual[edge ^ 1] += amount
                excess[other] += amount
                excess[source] -= amount

        self._global_relabel(source, sink, height, current)
        buckets = [[] for _ in range(2 * n + 1)]
        count = [0] * (2 * n + 1)
        top = -1
        for vertex, h in enumerate(height):
            count[h] += 1
            if vertex != source and vertex != sink and excess[vertex]:
                buckets[h].append(vertex)
                if h > top:
                    top = h
        work = 0
        threshold = 4 * len(to) + n

        while top >= 0:
            if not buckets[top]:
                top -= 1
                continue
            vertex = buckets[top].pop()
            if height[vertex] != top or not excess[vertex]:
                continue
            edges = graph[vertex]
            rest = excess[vertex]
            hv = height[vertex]
            index = current[vertex]
            while rest:
                if index == len(edges):
                    best = 2 * n
                    for edge in edges:
                        if residual[edge] and height[to[edge]] < best:
                            best = height[to[edge]]
                    count[hv] -= 1
                    old = hv
                    hv = best + 1
                    height[vertex] = hv
                    count[hv] += 1
                    index = 0
                    work += len(edges)
                    if old < n and not count[old]:
                        for other, h in enumerate(height):
                            if old < h < n:
                                count[h] -= 1
                                height[other] = n + 1
                                count[n + 1] += 1
                                current[other] = 0
                                if other != vertex and excess[other]:
                                    buckets[n + 1].append(other)
                                    if top < n + 1:
                                        top = n + 1
                        hv = height[vertex]
                    continue

                edge = edges[index]
                other = to[edge]
                capacity = residual[edge]
                if capacity and hv == height[other] + 1:
                    amount = rest if rest < capacity else capacity
                    residual[edge] -= amount
                    residual[edge ^ 1] += amount
                    rest -= amount
                    if not excess[other] and other != source and other != sink:
                        h = height[other]
                        buckets[h].append(other)
                        if h > top:
                            top = h
                    excess[other] += amount
                    if not rest:
                        break
                index += 1
                work += 1
            excess[vertex] = 0
            current[vertex] = index

            if work >= threshold:
                self._global_relabel(source, sink, height, current)
                buckets = [[] for _ in range(2 * n + 1)]
                count = [0] * (2 * n + 1)
                top = -1
                for other, h in enumerate(height):
                    count[h] += 1
                    if other != source and other != sink and excess[other]:
                        buckets[h].append(other)
                        if h > top:
                            top = h
                work = 0
        return excess[sink]


    def min_cut(self, source):
        if not 0 <= source < self.n:
            raise IndexError("vertex out of range")
        visited = bytearray(self.n)
        visited[source] = 1
        queue = [source]
        graph = self.graph
        to = self.to
        residual = self.capacity
        for vertex in queue:
            for edge in graph[vertex]:
                other = to[edge]
                if residual[edge] and not visited[other]:
                    visited[other] = 1
                    queue.append(other)
        return [bool(value) for value in visited]
