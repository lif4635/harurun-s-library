class MaxFlowGraph:
    __slots__ = ("n", "graph", "pos")

    def __init__(self, n):
        assert n >= 0
        self.n = n
        self.graph = [[] for _ in range(n)]
        self.pos = []

    def add_vertex(self):
        self.graph.append([])
        self.n += 1
        return self.n - 1

    def add_edge(self, source, target, capacity):
        assert 0 <= source < self.n and 0 <= target < self.n and capacity >= 0
        graph = self.graph
        source_id = len(graph[source])
        target_id = len(graph[target])
        if source == target:
            target_id += 1
        self.pos.append((source, source_id))
        graph[source].append([target, target_id, capacity])
        graph[target].append([source, source_id, 0])
        return len(self.pos) - 1

    def get_edge(self, i):
        source, index = self.pos[i]
        edge = self.graph[source][index]
        reverse = self.graph[edge[0]][edge[1]]
        return source, edge[0], edge[2] + reverse[2], reverse[2]

    def edges(self):
        return [self.get_edge(i) for i in range(len(self.pos))]

    def residual_graph(self, include_zero=False):
        """Return ``(to, residual_capacity)`` rows of the residual graph."""
        if include_zero:
            return [[(edge[0], edge[2]) for edge in row] for row in self.graph]
        return [
            [(edge[0], edge[2]) for edge in row if edge[2]]
            for row in self.graph
        ]

    def change_edge(self, i, capacity, flow):
        assert 0 <= flow <= capacity
        source, index = self.pos[i]
        edge = self.graph[source][index]
        reverse = self.graph[edge[0]][edge[1]]
        edge[2] = capacity - flow
        reverse[2] = flow

    def _send_one(self, source, sink, limit, level, current):
        graph = self.graph
        stack_v = [source]
        stack_e = []
        stack_cap = [limit]
        n = self.n
        while stack_v:
            v = stack_v[-1]
            if v == sink:
                flow = stack_cap[-1]
                for u, i in stack_e:
                    edge = graph[u][i]
                    edge[2] -= flow
                    graph[edge[0]][edge[1]][2] += flow
                return flow

            edges = graph[v]
            i = current[v]
            next_level = level[v] + 1
            while i < len(edges):
                edge = edges[i]
                if edge[2] and level[edge[0]] == next_level:
                    break
                i += 1
            current[v] = i
            if i == len(edges):
                level[v] = n
                stack_v.pop()
                stack_cap.pop()
                if stack_e:
                    parent, edge_id = stack_e.pop()
                    current[parent] = edge_id + 1
                continue

            edge = edges[i]
            stack_e.append((v, i))
            stack_v.append(edge[0])
            stack_cap.append(min(stack_cap[-1], edge[2]))
        return 0

    def flow(self, source, sink, flow_limit=None):
        assert 0 <= source < self.n and 0 <= sink < self.n and source != sink
        graph = self.graph
        if flow_limit is None:
            flow_limit = sum(edge[2] for edge in graph[source])
        assert flow_limit >= 0
        total = 0
        n = self.n
        while total < flow_limit:
            level = [-1] * n
            level[source] = 0
            que = [source]
            for v in que:
                next_level = level[v] + 1
                for edge in graph[v]:
                    if edge[2] and level[edge[0]] < 0:
                        level[edge[0]] = next_level
                        que.append(edge[0])
            if level[sink] < 0:
                break
            current = [0] * n
            while total < flow_limit:
                pushed = self._send_one(
                    source, sink, flow_limit - total, level, current
                )
                if pushed == 0:
                    break
                total += pushed
        return total

    max_flow = flow
    run = flow

    def min_cut(self, source):
        assert 0 <= source < self.n
        visited = [False] * self.n
        visited[source] = True
        que = [source]
        graph = self.graph
        for v in que:
            for edge in graph[v]:
                if edge[2] and not visited[edge[0]]:
                    visited[edge[0]] = True
                    que.append(edge[0])
        return visited

    def min_cut_edges(self, source):
        """Return original edges crossing the current source-side minimum cut.

        Each entry is ``(edge_id, source, target, capacity, flow)``.
        """
        reachable = self.min_cut(source)
        result = []
        for edge_id in range(len(self.pos)):
            first, second, capacity, flow = self.get_edge(edge_id)
            if reachable[first] and not reachable[second]:
                result.append((edge_id, first, second, capacity, flow))
        return result


MaxFlow = MaxFlowGraph


def feasible_circulation(n, edges):
    """各辺のlower以上upper以下を満たすcirculationを1つ返す。"""
    edges = list(edges)
    source = n
    sink = n + 1
    graph = MaxFlowGraph(n + 2)
    balance = [0] * n
    original = []
    for first, second, lower, upper in edges:
        if not 0 <= first < n or not 0 <= second < n:
            raise IndexError("edge endpoint is out of range")
        if not 0 <= lower <= upper:
            raise ValueError("edge bounds must satisfy 0 <= lower <= upper")
        original.append((graph.add_edge(first, second, upper - lower), lower))
        balance[first] -= lower
        balance[second] += lower
    demand = 0
    for vertex, value in enumerate(balance):
        if value > 0:
            graph.add_edge(source, vertex, value)
            demand += value
        elif value < 0:
            graph.add_edge(vertex, sink, -value)
    if graph.flow(source, sink) != demand:
        return None
    return [lower + graph.get_edge(edge_id)[3]
            for edge_id, lower in original]


def max_flow_with_bounds(n, edges, source, sink):
    """各辺のlower/upperを満たすsource-sink flowの最大値と辺flowを返す。"""
    if source == sink or not 0 <= source < n or not 0 <= sink < n:
        raise ValueError("source and sink must be distinct valid vertices")
    edges = list(edges)
    super_source = n
    super_sink = n + 1
    graph = MaxFlowGraph(n + 2)
    balance = [0] * n
    original = []
    upper_sum = 0
    for first, second, lower, upper in edges:
        if not 0 <= first < n or not 0 <= second < n:
            raise IndexError("edge endpoint is out of range")
        if not 0 <= lower <= upper:
            raise ValueError("edge bounds must satisfy 0 <= lower <= upper")
        original.append((graph.add_edge(first, second, upper - lower), lower))
        balance[first] -= lower
        balance[second] += lower
        upper_sum += upper
    bridge = graph.add_edge(sink, source, upper_sum + 1)
    auxiliary = []
    demand = 0
    for vertex, value in enumerate(balance):
        if value > 0:
            auxiliary.append(graph.add_edge(super_source, vertex, value))
            demand += value
        elif value < 0:
            auxiliary.append(graph.add_edge(vertex, super_sink, -value))
    if graph.flow(super_source, super_sink) != demand:
        return None
    base_flow = graph.get_edge(bridge)[3]
    graph.change_edge(bridge, 0, 0)
    for edge_id in auxiliary:
        graph.change_edge(edge_id, 0, 0)
    value = base_flow + graph.flow(source, sink)
    flows = [lower + graph.get_edge(edge_id)[3]
             for edge_id, lower in original]
    return value, flows
