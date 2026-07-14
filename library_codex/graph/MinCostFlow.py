from heapq import heappop, heappush


INF = float("inf")


class MinCostFlowGraph:
    __slots__ = ("n", "graph", "pos", "potential", "started")

    def __init__(self, n):
        assert n >= 0
        self.n = n
        self.graph = [[] for _ in range(n)]
        self.pos = []
        self.potential = [0] * n
        self.started = False

    def add_edge(self, source, target, capacity, cost):
        assert not self.started
        assert 0 <= source < self.n and 0 <= target < self.n
        assert capacity >= 0 and cost >= 0
        graph = self.graph
        source_id = len(graph[source])
        target_id = len(graph[target])
        if source == target:
            target_id += 1
        self.pos.append((source, source_id))
        graph[source].append([target, target_id, capacity, cost])
        graph[target].append([source, source_id, 0, -cost])
        return len(self.pos) - 1

    def get_edge(self, i):
        source, index = self.pos[i]
        edge = self.graph[source][index]
        reverse = self.graph[edge[0]][edge[1]]
        return source, edge[0], edge[2] + reverse[2], reverse[2], edge[3]

    def edges(self):
        return [self.get_edge(i) for i in range(len(self.pos))]

    def slope(self, source, sink, flow_limit=None):
        assert 0 <= source < self.n and 0 <= sink < self.n and source != sink
        graph = self.graph
        if flow_limit is None:
            flow_limit = sum(edge[2] for edge in graph[source])
        assert flow_limit >= 0
        self.started = True
        n = self.n
        potential = self.potential
        flow = 0
        cost = 0
        result = [(0, 0)]
        previous_cost = None

        while flow < flow_limit:
            dist = [INF] * n
            prev_v = [-1] * n
            prev_e = [-1] * n
            dist[source] = 0
            que = []
            que_zero = [source]
            while que_zero or que:
                if que_zero:
                    v = que_zero.pop()
                    d = dist[v]
                else:
                    d, v = heappop(que)
                if d != dist[v]:
                    continue
                pv = potential[v]
                for i, edge in enumerate(graph[v]):
                    if edge[2] == 0:
                        continue
                    nd = d + edge[3] + pv - potential[edge[0]]
                    if nd < dist[edge[0]]:
                        dist[edge[0]] = nd
                        prev_v[edge[0]] = v
                        prev_e[edge[0]] = i
                        if nd == d:
                            que_zero.append(edge[0])
                        else:
                            heappush(que, (nd, edge[0]))
            if dist[sink] == INF:
                break

            for v in range(n):
                if dist[v] != INF:
                    potential[v] += dist[v]
            add = flow_limit - flow
            v = sink
            while v != source:
                u = prev_v[v]
                add = min(add, graph[u][prev_e[v]][2])
                v = u
            v = sink
            while v != source:
                u = prev_v[v]
                edge = graph[u][prev_e[v]]
                edge[2] -= add
                graph[v][edge[1]][2] += add
                v = u

            unit_cost = potential[sink] - potential[source]
            flow += add
            cost += add * unit_cost
            if unit_cost == previous_cost:
                result[-1] = (flow, cost)
            else:
                result.append((flow, cost))
                previous_cost = unit_cost
        return result

    def flow(self, source, sink, flow_limit=None):
        return self.slope(source, sink, flow_limit)[-1]

    min_cost_flow = flow


MinCostFlow = MinCostFlowGraph
