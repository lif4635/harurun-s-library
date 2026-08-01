"""High-performance and undirected cut algorithms.

The implementations are iterative and use only the Python standard library.
``PushRelabelMaxFlow`` is an alternative to Dinic whose performance profile is
different; benchmark both for a fixed problem family when speed is critical.
"""

from collections import deque


class PushRelabelMaxFlow:
    """FIFO push-relabel max flow with periodic global relabeling."""

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
        if not (0 <= flow <= capacity):
            raise ValueError("flow must satisfy 0 <= flow <= capacity")
        _, edge = self.position[index]
        self.capacity[edge] = capacity - flow
        self.capacity[edge ^ 1] = flow

    def _global_relabel(self, source, sink, height, current):
        n = self.n
        unreachable = n + 1
        for vertex in range(n):
            height[vertex] = unreachable
            current[vertex] = 0
        height[sink] = 0
        queue = [sink]
        graph = self.graph
        to = self.to
        residual = self.capacity
        for vertex in queue:
            next_height = height[vertex] + 1
            for edge in graph[vertex]:
                other = to[edge]
                if height[other] == unreachable and residual[edge ^ 1]:
                    height[other] = next_height
                    queue.append(other)
        height[source] = n

    def flow(self, source, sink, flow_limit=None):
        """Add and return flow up to ``flow_limit`` on the residual graph."""
        n = self.n
        if not (0 <= source < n and 0 <= sink < n):
            raise IndexError("vertex out of range")
        if source == sink:
            raise ValueError("source and sink must differ")
        if flow_limit is not None and flow_limit < 0:
            raise ValueError("flow limit must be nonnegative")
        if flow_limit is None:
            return self._flow_unlimited(source, sink)
        if flow_limit == 0:
            return 0

        # A temporary super-source turns the limit into an ordinary edge
        # capacity.  This avoids losing budget when an initially saturated
        # source edge later returns excess to the source.
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
        graph = self.graph
        to = self.to
        residual = self.capacity
        excess = [0] * n
        height = [0] * n
        current = [0] * n

        # A preflow turns all residual edges out of the source into active
        # vertices. Reverse residual edges make repeated calls valid too.
        for edge in graph[source]:
            if to[edge] == source:
                continue
            amount = residual[edge]
            if amount:
                residual[edge] = 0
                residual[edge ^ 1] += amount
                excess[to[edge]] += amount
                excess[source] -= amount

        self._global_relabel(source, sink, height, current)
        active = bytearray(n)
        queue = deque()
        for vertex in range(n):
            if vertex != source and vertex != sink and excess[vertex]:
                active[vertex] = 1
                queue.append(vertex)

        edge_count = max(1, len(to))
        work = 0
        global_relabel_after = max(n, edge_count << 1)

        while queue:
            vertex = queue.popleft()
            active[vertex] = 0
            edges = graph[vertex]

            while excess[vertex]:
                index = current[vertex]
                if index == len(edges):
                    best = 2 * n + 1
                    for edge in edges:
                        if residual[edge] and height[to[edge]] < best:
                            best = height[to[edge]]
                    height[vertex] = best + 1
                    current[vertex] = 0
                    work += len(edges)
                    continue

                edge = edges[index]
                other = to[edge]
                if residual[edge] and height[vertex] == height[other] + 1:
                    amount = min(excess[vertex], residual[edge])
                    residual[edge] -= amount
                    residual[edge ^ 1] += amount
                    excess[vertex] -= amount
                    was_empty = excess[other] == 0
                    excess[other] += amount
                    if (
                        was_empty
                        and other != source
                        and other != sink
                        and not active[other]
                    ):
                        active[other] = 1
                        queue.append(other)
                else:
                    current[vertex] = index + 1
                    work += 1

            if work >= global_relabel_after and queue:
                self._global_relabel(source, sink, height, current)
                queue.clear()
                active = bytearray(n)
                for other in range(n):
                    if other != source and other != sink and excess[other]:
                        active[other] = 1
                        queue.append(other)
                work = 0

        return excess[sink]

    max_flow = flow
    run = flow

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


def gomory_hu_tree(n, edges, flow_class=PushRelabelMaxFlow):
    """Return an undirected Gomory--Hu cut tree as ``(u, v, cut)`` edges.

    Parallel edges and zero-capacity edges are accepted. ``edges`` is consumed
    once and materialized because the max-flow graph is rebuilt ``n - 1`` times.
    """
    if n < 0:
        raise ValueError("number of vertices must be nonnegative")
    edges = list(edges)
    for source, target, capacity in edges:
        if not (0 <= source < n and 0 <= target < n):
            raise IndexError("vertex out of range")
        if capacity < 0:
            raise ValueError("capacity must be nonnegative")
    if n <= 1:
        return []

    parent = [0] * n
    value = [0] * n
    for source in range(1, n):
        sink = parent[source]
        flow = flow_class(n)
        for left, right, capacity in edges:
            if left != right and capacity:
                flow.add_edge(left, right, capacity)
                flow.add_edge(right, left, capacity)
        cut_value = flow.flow(source, sink)
        side = flow.min_cut(source)

        for vertex in range(source + 1, n):
            if parent[vertex] == sink and side[vertex]:
                parent[vertex] = source
        sink_parent = parent[sink]
        if side[sink_parent]:
            parent[source] = sink_parent
            parent[sink] = source
            value[source] = value[sink]
            value[sink] = cut_value
        else:
            value[source] = cut_value

    return [(vertex, parent[vertex], value[vertex]) for vertex in range(1, n)]


def stoer_wagner_min_cut(n, edges):
    """Return ``(cut_value, one_side)`` for an undirected weighted graph.

    This dense ``O(V^3)`` implementation is useful when running ``V - 1``
    max-flow computations would be more expensive. The graph may be
    disconnected, in which case the returned minimum value is zero.
    """
    if n < 0:
        raise ValueError("number of vertices must be nonnegative")
    if n == 0:
        return 0, []
    matrix = [[0] * n for _ in range(n)]
    for source, target, weight in edges:
        if not (0 <= source < n and 0 <= target < n):
            raise IndexError("vertex out of range")
        if weight < 0:
            raise ValueError("weight must be nonnegative")
        if source != target:
            matrix[source][target] += weight
            matrix[target][source] += weight
    if n == 1:
        return 0, [0]

    vertices = list(range(n))
    groups = [[vertex] for vertex in range(n)]
    best_value = None
    best_side = []

    while len(vertices) > 1:
        weights = [0] * n
        used = bytearray(n)
        previous = -1
        for step in range(len(vertices)):
            selected = -1
            selected_weight = -1
            for vertex in vertices:
                if not used[vertex] and weights[vertex] > selected_weight:
                    selected = vertex
                    selected_weight = weights[vertex]

            if step + 1 == len(vertices):
                if best_value is None or selected_weight < best_value:
                    best_value = selected_weight
                    best_side = groups[selected][:]
                for vertex in vertices:
                    if vertex != selected and vertex != previous:
                        merged = matrix[previous][vertex] + matrix[selected][vertex]
                        matrix[previous][vertex] = merged
                        matrix[vertex][previous] = merged
                groups[previous].extend(groups[selected])
                vertices.remove(selected)
                break

            used[selected] = 1
            previous = selected
            selected_row = matrix[selected]
            for vertex in vertices:
                if not used[vertex]:
                    weights[vertex] += selected_row[vertex]

    return best_value, best_side


FastMaxFlow = PushRelabelMaxFlow
