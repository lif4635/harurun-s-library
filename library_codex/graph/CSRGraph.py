"""Flat CSR graph storage and iterative graph algorithms for PyPy.

CSR avoids one Python list per adjacency row and one tuple per arc.  The graph
is immutable after construction, which lets hot algorithms use flat arrays
without entry-shape checks.
"""

from collections import deque
import heapq


INF = float("inf")


class CSRGraph:
    """Immutable directed or undirected compressed sparse row graph."""

    __slots__ = ("n", "m", "arc_count", "directed", "start", "to", "weight", "edge_id")

    def __init__(self, n, edges=(), directed=True):
        if n < 0:
            raise ValueError("number of vertices must be nonnegative")
        records = edges if isinstance(edges, (list, tuple)) else list(edges)
        m = len(records)
        arc_count = m if directed else m << 1
        start = [0] * (n + 1)
        for entry in records:
            if len(entry) < 2:
                raise ValueError("each edge needs at least two endpoints")
            source = entry[0]
            target = entry[1]
            if not (0 <= source < n and 0 <= target < n):
                raise IndexError("vertex out of range")
            start[source + 1] += 1
            if not directed:
                start[target + 1] += 1
        for vertex in range(n):
            start[vertex + 1] += start[vertex]

        cursor = start[:-1].copy()
        to = [0] * arc_count
        weight = [0] * arc_count
        edge_id = [0] * arc_count
        for edge, entry in enumerate(records):
            source = entry[0]
            target = entry[1]
            edge_weight = entry[2] if len(entry) >= 3 else 1
            index = cursor[source]
            cursor[source] = index + 1
            to[index] = target
            weight[index] = edge_weight
            edge_id[index] = edge
            if not directed:
                index = cursor[target]
                cursor[target] = index + 1
                to[index] = source
                weight[index] = edge_weight
                edge_id[index] = edge

        self.n = n
        self.m = m
        self.arc_count = arc_count
        self.directed = directed
        self.start = start
        self.to = to
        self.weight = weight
        self.edge_id = edge_id

    @classmethod
    def from_adjacency(cls, adjacency, directed=True):
        """Build from an adjacency list.

        A directed adjacency list contains every arc once.  An undirected
        adjacency list must be symmetric: every entry, including each
        parallel edge, needs one matching reverse entry.  A self-loop is
        therefore represented by two identical entries.
        """
        n = len(adjacency)
        edges = []
        if not directed:
            pending = {}
            for source, row in enumerate(adjacency):
                for entry in row:
                    if isinstance(entry, int):
                        target = entry
                        edge_weight = 1
                    else:
                        target = entry[0]
                        edge_weight = entry[1]
                    if not 0 <= target < n:
                        raise IndexError("vertex out of range")
                    reverse = (target, source, edge_weight)
                    count = pending.get(reverse, 0)
                    if count:
                        if count == 1:
                            del pending[reverse]
                        else:
                            pending[reverse] = count - 1
                        edges.append((source, target, edge_weight))
                    else:
                        key = (source, target, edge_weight)
                        pending[key] = pending.get(key, 0) + 1
            if pending:
                raise ValueError(
                    "undirected adjacency must contain one reverse entry "
                    "for every edge"
                )
            return cls(n, edges, directed=False)

        for source, row in enumerate(adjacency):
            for entry in row:
                if isinstance(entry, int):
                    edges.append((source, entry, 1))
                else:
                    edges.append((source, entry[0], entry[1]))
        return cls(n, edges, directed)

    def transpose(self):
        """Return the edge-reversed CSR graph in linear time."""
        if not self.directed:
            return self
        n = self.n
        start = [0] * (n + 1)
        to = self.to
        for target in to:
            start[target + 1] += 1
        for vertex in range(n):
            start[vertex + 1] += start[vertex]
        cursor = start[:-1].copy()
        reverse_to = [0] * self.arc_count
        reverse_weight = [0] * self.arc_count
        reverse_edge_id = [0] * self.arc_count
        for source in range(n):
            for index in range(self.start[source], self.start[source + 1]):
                target = to[index]
                reverse_index = cursor[target]
                cursor[target] = reverse_index + 1
                reverse_to[reverse_index] = source
                reverse_weight[reverse_index] = self.weight[index]
                reverse_edge_id[reverse_index] = self.edge_id[index]
        result = object.__new__(CSRGraph)
        result.n = n
        result.m = self.m
        result.arc_count = self.arc_count
        result.directed = True
        result.start = start
        result.to = reverse_to
        result.weight = reverse_weight
        result.edge_id = reverse_edge_id
        return result

    def neighbors(self, vertex):
        """Yield ``(to, weight, edge_id)`` triples for one vertex."""
        if not 0 <= vertex < self.n:
            raise IndexError("vertex out of range")
        to = self.to
        weight = self.weight
        edge_id = self.edge_id
        for index in range(self.start[vertex], self.start[vertex + 1]):
            yield to[index], weight[index], edge_id[index]

    def __len__(self):
        return self.n


def _as_csr(graph, directed):
    if isinstance(graph, CSRGraph):
        return graph
    return CSRGraph.from_adjacency(graph, directed=directed)


def dijkstra_csr(graph, start=0, goal=None, check_nonnegative=True):
    """Dijkstra on a CSR graph or adjacency list."""
    graph = _as_csr(graph, directed=True)
    n = graph.n
    if not 0 <= start < n:
        raise IndexError("start vertex out of range")
    if goal is not None and not 0 <= goal < n:
        raise IndexError("goal vertex out of range")
    weight = graph.weight
    if check_nonnegative and any(value < 0 for value in weight):
        raise ValueError("Dijkstra requires nonnegative weights")

    distance = [INF] * n
    previous = [-1] * n
    distance[start] = 0
    heap = [(0, start)]
    push = heapq.heappush
    pop = heapq.heappop
    offsets = graph.start
    to = graph.to
    while heap:
        current, vertex = pop(heap)
        if current != distance[vertex]:
            continue
        if vertex == goal:
            break
        for index in range(offsets[vertex], offsets[vertex + 1]):
            other = to[index]
            next_distance = current + weight[index]
            if next_distance < distance[other]:
                distance[other] = next_distance
                previous[other] = vertex
                push(heap, (next_distance, other))
    return distance, previous


def zero_one_bfs_csr(graph, start=0, check_weights=True):
    """0-1 BFS on a CSR graph or adjacency list."""
    graph = _as_csr(graph, directed=True)
    n = graph.n
    if not 0 <= start < n:
        raise IndexError("start vertex out of range")
    weight = graph.weight
    if check_weights and any(value != 0 and value != 1 for value in weight):
        raise ValueError("edge weight must be 0 or 1")
    distance = [INF] * n
    previous = [-1] * n
    distance[start] = 0
    queue = deque([start])
    offsets = graph.start
    to = graph.to
    while queue:
        vertex = queue.popleft()
        current = distance[vertex]
        for index in range(offsets[vertex], offsets[vertex + 1]):
            other = to[index]
            edge_weight = weight[index]
            next_distance = current + edge_weight
            if next_distance < distance[other]:
                distance[other] = next_distance
                previous[other] = vertex
                if edge_weight:
                    queue.append(other)
                else:
                    queue.appendleft(other)
    return distance, previous


def bfs_csr(graph, start=0, goal=None):
    """Unweighted BFS on a CSR graph or adjacency list."""
    graph = _as_csr(graph, directed=True)
    n = graph.n
    if not 0 <= start < n:
        raise IndexError("start vertex out of range")
    if goal is not None and not 0 <= goal < n:
        raise IndexError("goal vertex out of range")
    distance = [-1] * n
    previous = [-1] * n
    distance[start] = 0
    queue = deque([start])
    offsets = graph.start
    to = graph.to
    while queue:
        vertex = queue.popleft()
        if vertex == goal:
            break
        next_distance = distance[vertex] + 1
        for index in range(offsets[vertex], offsets[vertex + 1]):
            other = to[index]
            if distance[other] < 0:
                distance[other] = next_distance
                previous[other] = vertex
                queue.append(other)
    return distance, previous


def topological_sort_csr(graph, lexicographical=False):
    """Topologically sort a directed CSR graph or adjacency list."""
    graph = _as_csr(graph, directed=True)
    if not graph.directed:
        raise ValueError("topological sort requires a directed graph")
    n = graph.n
    indegree = [0] * n
    to = graph.to
    for other in to:
        indegree[other] += 1
    offsets = graph.start
    result = []
    if lexicographical:
        queue = [vertex for vertex in range(n) if indegree[vertex] == 0]
        heapq.heapify(queue)
        while queue:
            vertex = heapq.heappop(queue)
            result.append(vertex)
            for index in range(offsets[vertex], offsets[vertex + 1]):
                other = to[index]
                indegree[other] -= 1
                if indegree[other] == 0:
                    heapq.heappush(queue, other)
    else:
        queue = deque(vertex for vertex in range(n) if indegree[vertex] == 0)
        while queue:
            vertex = queue.popleft()
            result.append(vertex)
            for index in range(offsets[vertex], offsets[vertex + 1]):
                other = to[index]
                indegree[other] -= 1
                if indegree[other] == 0:
                    queue.append(other)
    return result if len(result) == n else None


def connected_components_csr(graph):
    """Find components of an undirected CSR graph or symmetric adjacency list."""
    graph = _as_csr(graph, directed=False)
    if graph.directed:
        raise ValueError("connected components require an undirected graph")
    n = graph.n
    component = [-1] * n
    groups = []
    offsets = graph.start
    to = graph.to
    for root in range(n):
        if component[root] >= 0:
            continue
        group_id = len(groups)
        component[root] = group_id
        group = []
        stack = [root]
        while stack:
            vertex = stack.pop()
            group.append(vertex)
            for index in range(offsets[vertex], offsets[vertex + 1]):
                other = to[index]
                if component[other] < 0:
                    component[other] = group_id
                    stack.append(other)
        groups.append(group)
    return component, groups


def bipartite_coloring_csr(graph):
    """Color an undirected CSR graph or symmetric adjacency list with 0/1."""
    graph = _as_csr(graph, directed=False)
    if graph.directed:
        raise ValueError("bipartite coloring requires an undirected graph")
    n = graph.n
    color = [-1] * n
    offsets = graph.start
    to = graph.to
    for root in range(n):
        if color[root] >= 0:
            continue
        color[root] = 0
        queue = deque([root])
        while queue:
            vertex = queue.popleft()
            next_color = color[vertex] ^ 1
            for index in range(offsets[vertex], offsets[vertex + 1]):
                other = to[index]
                if color[other] < 0:
                    color[other] = next_color
                    queue.append(other)
                elif color[other] != next_color:
                    return None
    return color


def scc_ids_csr(graph):
    """Find SCCs of a directed CSR graph or adjacency list."""
    graph = _as_csr(graph, directed=True)
    if not graph.directed:
        raise ValueError("SCC requires a directed graph")
    n = graph.n
    offsets = graph.start
    to = graph.to
    seen = bytearray(n)
    order = []
    for root in range(n):
        if seen[root]:
            continue
        seen[root] = 1
        stack_vertex = [root]
        stack_index = [offsets[root]]
        while stack_vertex:
            vertex = stack_vertex[-1]
            index = stack_index[-1]
            if index == offsets[vertex + 1]:
                order.append(vertex)
                stack_vertex.pop()
                stack_index.pop()
                continue
            stack_index[-1] = index + 1
            other = to[index]
            if not seen[other]:
                seen[other] = 1
                stack_vertex.append(other)
                stack_index.append(offsets[other])

    reverse = graph.transpose()
    reverse_offsets = reverse.start
    reverse_to = reverse.to
    component = [-1] * n
    count = 0
    for root in reversed(order):
        if component[root] >= 0:
            continue
        component[root] = count
        stack = [root]
        while stack:
            vertex = stack.pop()
            for index in range(reverse_offsets[vertex], reverse_offsets[vertex + 1]):
                other = reverse_to[index]
                if component[other] < 0:
                    component[other] = count
                    stack.append(other)
        count += 1
    return count, component


class CSRSCC:
    """SCC result compatible with the existing high-level SCC object."""

    __slots__ = ("n", "graph", "component", "groups", "dag", "count")

    def __init__(self, graph, build_dag=True):
        graph = _as_csr(graph, directed=True)
        count, component = scc_ids_csr(graph)
        groups = [[] for _ in range(count)]
        for vertex, group in enumerate(component):
            groups[group].append(vertex)
        if build_dag:
            dag_sets = [set() for _ in range(count)]
            offsets = graph.start
            to = graph.to
            for vertex in range(graph.n):
                first = component[vertex]
                for index in range(offsets[vertex], offsets[vertex + 1]):
                    second = component[to[index]]
                    if first != second:
                        dag_sets[first].add(second)
            dag = [list(row) for row in dag_sets]
        else:
            dag = None
        self.n = graph.n
        self.graph = graph
        self.component = component
        self.groups = groups
        self.dag = dag
        self.count = count

    def same(self, first, second):
        return self.component[first] == self.component[second]

    def __getitem__(self, vertex):
        return self.component[vertex]


def scc_csr(graph):
    solver = CSRSCC(graph, build_dag=False)
    return solver.component, solver.groups


class CSRLowLink:
    """Iterative LowLink over an undirected CSR graph or adjacency list."""

    __slots__ = (
        "n", "graph", "edge_from", "edge_to", "order", "ord", "low",
        "parent", "parent_edge", "is_articulation", "articulation",
        "is_bridge", "bridge_ids", "bridges", "bridge",
    )

    def __init__(self, graph, edges=None):
        if isinstance(graph, int):
            n = graph
            records = () if edges is None else edges
            records = records if isinstance(records, (list, tuple)) else list(records)
            edge_from = [entry[0] for entry in records]
            edge_to = [entry[1] for entry in records]
            graph = CSRGraph(n, records, directed=False)
        else:
            if edges is not None:
                raise TypeError("edges is only used with a vertex count")
            graph = _as_csr(graph, directed=False)
            if graph.directed:
                raise ValueError("LowLink requires an undirected graph")
            n = graph.n
            edge_from = [0] * graph.m
            edge_to = [0] * graph.m
            seen_edge = bytearray(graph.m)
            for source in range(n):
                for index in range(graph.start[source], graph.start[source + 1]):
                    edge = graph.edge_id[index]
                    if not seen_edge[edge]:
                        seen_edge[edge] = 1
                        edge_from[edge] = source
                        edge_to[edge] = graph.to[index]
        offsets = graph.start
        to = graph.to
        arc_edge_id = graph.edge_id
        order = [-1] * n
        low = [-1] * n
        parent = [-1] * n
        parent_edge = [-1] * n
        current = offsets[:-1].copy()
        child_count = [0] * n
        is_articulation = [False] * n
        is_bridge = [False] * len(edge_from)
        bridge_ids = []
        timer = 0

        for root in range(n):
            if order[root] >= 0:
                continue
            order[root] = timer
            low[root] = timer
            timer += 1
            stack = [root]
            while stack:
                vertex = stack[-1]
                index = current[vertex]
                if index < offsets[vertex + 1]:
                    current[vertex] = index + 1
                    edge = arc_edge_id[index]
                    if edge == parent_edge[vertex]:
                        continue
                    other = to[index]
                    if order[other] < 0:
                        parent[other] = vertex
                        parent_edge[other] = edge
                        child_count[vertex] += 1
                        order[other] = timer
                        low[other] = timer
                        timer += 1
                        stack.append(other)
                    elif order[other] < low[vertex]:
                        low[vertex] = order[other]
                    continue

                stack.pop()
                previous = parent[vertex]
                if previous < 0:
                    if child_count[vertex] >= 2:
                        is_articulation[vertex] = True
                    continue
                if low[vertex] < low[previous]:
                    low[previous] = low[vertex]
                if low[vertex] > order[previous]:
                    edge = parent_edge[vertex]
                    is_bridge[edge] = True
                    bridge_ids.append(edge)
                if parent[previous] >= 0 and low[vertex] >= order[previous]:
                    is_articulation[previous] = True

        bridges = []
        for edge in bridge_ids:
            source = edge_from[edge]
            target = edge_to[edge]
            bridges.append((source, target) if source < target else (target, source))
        self.n = n
        self.graph = graph
        self.edge_from = edge_from
        self.edge_to = edge_to
        self.order = order
        self.ord = order
        self.low = low
        self.parent = parent
        self.parent_edge = parent_edge
        self.is_articulation = is_articulation
        self.articulation = [v for v in range(n) if is_articulation[v]]
        self.is_bridge = is_bridge
        self.bridge_ids = bridge_ids
        self.bridges = bridges
        self.bridge = bridges

    def get_edge(self, edge_id):
        return self.edge_from[edge_id], self.edge_to[edge_id]


FastDijkstra = dijkstra_csr
FastLowLink = CSRLowLink
