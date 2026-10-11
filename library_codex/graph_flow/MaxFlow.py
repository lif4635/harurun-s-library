class MaxFlowGraph:
    __slots__ = ("n", "graph", "to", "capacity")

    def __init__(self, n):
        assert n >= 0
        self.n = n
        self.graph = [[] for _ in range(n)]
        self.to = []
        self.capacity = []

    def add_vertex(self):
        self.graph.append([])
        self.n += 1
        return self.n - 1

    def add_edge(self, source, target, capacity):
        assert 0 <= source < self.n and 0 <= target < self.n and capacity >= 0
        graph = self.graph
        edge = len(self.to)
        graph[source].append(edge)
        graph[target].append(edge + 1)
        self.to.extend((target, source))
        self.capacity.extend((capacity, 0))
        return edge >> 1

    def get_edge(self, i):
        edge = i * 2
        capacity = self.capacity
        return self.to[edge + 1], self.to[edge], capacity[edge] + capacity[edge + 1], capacity[edge + 1]

    def edges(self):
        return [self.get_edge(i) for i in range(len(self.to) >> 1)]

    def residual_graph(self, include_zero=False):
        """Return ``(to, residual_capacity)`` rows of the residual graph."""
        if include_zero:
            return [[(self.to[edge], self.capacity[edge]) for edge in row] for row in self.graph]
        return [
            [(self.to[edge], self.capacity[edge]) for edge in row if self.capacity[edge]]
            for row in self.graph
        ]

    def change_edge(self, i, capacity, flow):
        assert 0 <= flow <= capacity
        edge = i * 2
        self.capacity[edge] = capacity - flow
        self.capacity[edge + 1] = flow

    def flow(self, source, sink, flow_limit=None):
        assert 0 <= source < self.n and 0 <= sink < self.n and source != sink
        graph = self.graph
        to = self.to
        capacity = self.capacity
        if flow_limit is None:
            flow_limit = sum(capacity[edge] for edge in graph[source])
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
                    other = to[edge]
                    if capacity[edge] and level[other] < 0:
                        level[other] = next_level
                        que.append(other)
                if level[sink] >= 0:
                    break
            if level[sink] < 0:
                break
            current = [0] * n
            vertices = [sink]
            path = []
            limits = [flow_limit - total]
            sent = [0]
            while vertices:
                v = vertices[-1]
                rest = limits[-1] - sent[-1]
                if v == source:
                    sent[-1] = limits[-1]
                elif rest:
                    row = graph[v]
                    index = current[v]
                    wanted = level[v] - 1
                    while index < len(row):
                        edge = row[index]
                        if capacity[edge ^ 1] and level[to[edge]] == wanted:
                            break
                        index += 1
                    current[v] = index
                    if index < len(row):
                        path.append(edge)
                        vertices.append(to[edge])
                        available = capacity[edge ^ 1]
                        limits.append(rest if rest < available else available)
                        sent.append(0)
                        continue
                    level[v] = n
                pushed = sent.pop()
                vertices.pop()
                limits.pop()
                if path:
                    edge = path.pop()
                    capacity[edge] += pushed
                    capacity[edge ^ 1] -= pushed
                    sent[-1] += pushed
                    if sent[-1] < limits[-1]:
                        current[vertices[-1]] += 1
                else:
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
        to = self.to
        capacity = self.capacity
        for v in que:
            for edge in graph[v]:
                other = to[edge]
                if capacity[edge] and not visited[other]:
                    visited[other] = True
                    que.append(other)
        return visited

    def min_cut_edges(self, source):
        """Return original edges crossing the current source-side minimum cut.

        Each entry is ``(edge_id, source, target, capacity, flow)``.
        """
        reachable = self.min_cut(source)
        result = []
        for edge_id in range(len(self.to) >> 1):
            first, second, capacity, flow = self.get_edge(edge_id)
            if reachable[first] and not reachable[second]:
                result.append((edge_id, first, second, capacity, flow))
        return result

    def flow_value(self, source):
        """現在のflowのsourceから外へ出る正味流量を返す。"""
        if not 0 <= source < self.n:
            raise IndexError("source is outside the graph")
        value = 0
        for edge_id in range(len(self.to) >> 1):
            first, second, _, flow = self.get_edge(edge_id)
            if first == source:
                value += flow
            if second == source:
                value -= flow
        return value

    def flow_paths(self, source, sink):
        """現在の正のflowをsource-sink pathへ分解する。"""
        if not 0 <= source < self.n or not 0 <= sink < self.n:
            raise IndexError("source or sink is outside the graph")
        if source == sink:
            raise ValueError("source and sink must be distinct")
        edge_data = self.edges()
        remaining = [edge[3] for edge in edge_data]
        outgoing = [[] for _ in range(self.n)]
        for edge_id, edge in enumerate(edge_data):
            if remaining[edge_id]:
                outgoing[edge[0]].append(edge_id)
        result = []
        while True:
            parent_edge = [-1] * self.n
            parent_edge[source] = -2
            queue = [source]
            for vertex in queue:
                if vertex == sink:
                    break
                for edge_id in outgoing[vertex]:
                    if remaining[edge_id] == 0:
                        continue
                    target = edge_data[edge_id][1]
                    if parent_edge[target] == -1:
                        parent_edge[target] = edge_id
                        queue.append(target)
            if parent_edge[sink] == -1:
                break
            edge_ids = []
            vertex = sink
            amount = None
            while vertex != source:
                edge_id = parent_edge[vertex]
                edge_ids.append(edge_id)
                flow = remaining[edge_id]
                if amount is None or flow < amount:
                    amount = flow
                vertex = edge_data[edge_id][0]
            edge_ids.reverse()
            vertices = [source]
            for edge_id in edge_ids:
                remaining[edge_id] -= amount
                vertices.append(edge_data[edge_id][1])
            result.append((amount, vertices, edge_ids))
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
