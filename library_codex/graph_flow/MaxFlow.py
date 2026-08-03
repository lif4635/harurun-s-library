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


MaxFlow = MaxFlowGraph
