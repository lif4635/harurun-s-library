from collections import deque

from library_codex.graph.MaxFlow import MaxFlowGraph


class MinCostBFlow:
    __slots__ = (
        "n",
        "edge_data",
        "supply",
        "dual",
        "graph",
        "positions",
        "max_cost",
        "solved",
    )

    def __init__(self, vertex_count):
        if vertex_count < 0:
            raise ValueError("vertex_count must be nonnegative")
        self.n = vertex_count
        self.edge_data = []
        self.supply = [0] * vertex_count
        self.dual = [0] * vertex_count
        self.graph = [[] for _ in range(vertex_count)]
        self.positions = []
        self.max_cost = 0
        self.solved = False

    def add_edge(self, source, target, lower, upper, cost):
        if self.solved:
            raise RuntimeError("cannot add edges after run")
        if not 0 <= source < self.n or not 0 <= target < self.n:
            raise ValueError("vertex index out of range")
        if lower > upper:
            raise ValueError("lower must not exceed upper")
        self.edge_data.append([source, target, lower, upper, cost, 0])
        self.max_cost = max(self.max_cost, abs(cost))
        return len(self.edge_data) - 1

    def add_supply(self, vertex, amount):
        if self.solved:
            raise RuntimeError("cannot change supply after run")
        if not 0 <= vertex < self.n:
            raise ValueError("vertex index out of range")
        self.supply[vertex] += amount

    add_excess = add_supply

    def add_demand(self, vertex, amount):
        self.add_supply(vertex, -amount)

    def _add_residual_edge(self, source, target, forward, backward, cost):
        graph = self.graph
        source_index = len(graph[source])
        target_index = len(graph[target])
        if source == target:
            target_index += 1
        self.positions.append((source, source_index))
        graph[source].append([target, target_index, forward, cost])
        graph[target].append([source, source_index, backward, -cost])

    def _refine(self, epsilon):
        n = self.n
        graph = self.graph
        dual = self.dual
        excess = [0] * n

        def push(source, edge, amount):
            excess[source] -= amount
            target = edge[0]
            excess[target] += amount
            graph[target][edge[1]][2] += amount
            edge[2] -= amount

        for source in range(n):
            source_dual = dual[source]
            for edge in graph[source]:
                if edge[2] and edge[3] + source_dual - dual[edge[0]] < 0:
                    push(source, edge, edge[2])
        queued = [False] * n
        queue = deque()
        for vertex in range(n):
            if excess[vertex] > 0:
                queued[vertex] = True
                queue.append(vertex)
        current = [0] * n
        while queue:
            vertex = queue.popleft()
            queued[vertex] = False
            edges = graph[vertex]
            index = current[vertex]
            while index < len(edges) and excess[vertex] > 0:
                edge = edges[index]
                if (
                    edge[2]
                    and edge[3] + dual[vertex] - dual[edge[0]] < 0
                ):
                    target = edge[0]
                    was_positive = excess[target] > 0
                    push(vertex, edge, min(excess[vertex], edge[2]))
                    if excess[target] > 0 and not was_positive and not queued[target]:
                        queued[target] = True
                        queue.append(target)
                if edge[2] == 0 or (
                    edge[3] + dual[vertex] - dual[edge[0]] >= 0
                ):
                    index += 1
            current[vertex] = index
            if excess[vertex] > 0:
                decrease = None
                source_dual = dual[vertex]
                for edge in edges:
                    if edge[2]:
                        value = (
                            epsilon
                            + edge[3]
                            + source_dual
                            - dual[edge[0]]
                        )
                        if decrease is None or value < decrease:
                            decrease = value
                if decrease is None:
                    raise ArithmeticError("positive excess has no residual edge")
                dual[vertex] -= decrease
                current[vertex] = 0
                if not queued[vertex]:
                    queued[vertex] = True
                    queue.append(vertex)
        next_epsilon = 0
        for source in range(n):
            source_dual = dual[source]
            for edge in graph[source]:
                if edge[2]:
                    next_epsilon = max(
                        next_epsilon,
                        -(edge[3] + source_dual - dual[edge[0]]),
                    )
        return next_epsilon

    def run(self):
        if self.solved:
            raise RuntimeError("run may only be called once")
        self.solved = True
        if self.n == 0:
            return (not self.edge_data, 0)
        balance = self.supply[:]
        feasibility = MaxFlowGraph(self.n + 2)
        super_source = self.n
        super_sink = self.n + 1
        for source, target, lower, upper, _, _ in self.edge_data:
            balance[target] += lower
            balance[source] -= lower
            feasibility.add_edge(source, target, upper - lower)
        positive = 0
        negative = 0
        for vertex, value in enumerate(balance):
            if value > 0:
                positive += value
                feasibility.add_edge(super_source, vertex, value)
            elif value < 0:
                negative -= value
                feasibility.add_edge(vertex, super_sink, -value)
        if positive != negative or feasibility.flow(
            super_source, super_sink, positive
        ) != positive:
            return False, 0
        scale = self.n
        for edge_id, data in enumerate(self.edge_data):
            source, target, lower, upper, cost, _ = data
            _, _, capacity, flow = feasibility.get_edge(edge_id)
            self._add_residual_edge(
                source,
                target,
                capacity - flow,
                flow,
                cost * scale,
            )
        epsilon = self.max_cost * scale + 1
        while epsilon > 1:
            epsilon = max(epsilon >> 2, 1)
            epsilon = self._refine(epsilon)
        total_cost = 0
        for edge_id, data in enumerate(self.edge_data):
            source, position = self.positions[edge_id]
            flow = data[3] - self.graph[source][position][2]
            data[5] = flow
            total_cost += flow * data[4]
        dual = [0] * self.n
        while True:
            changed = False
            for source in range(self.n):
                for target, _, capacity, scaled_cost in self.graph[source]:
                    if capacity:
                        value = dual[source] + scaled_cost // scale
                        if value < dual[target]:
                            dual[target] = value
                            changed = True
            if not changed:
                break
        self.dual = dual
        return True, total_cost

    def get_flow(self, edge_id):
        if not self.solved:
            raise RuntimeError("run must be called first")
        return self.edge_data[edge_id][5]

    def get_edge(self, edge_id):
        source, target, lower, upper, cost, flow = self.edge_data[edge_id]
        return source, target, lower, upper, cost, flow

    def edges(self):
        return [self.get_edge(index) for index in range(len(self.edge_data))]


MinimumCostBFlow = MinCostBFlow
