class LowLink:
    __slots__ = (
        "n", "graph", "edge_from", "edge_to", "order", "ord", "low",
        "parent", "parent_edge", "is_articulation", "articulation",
        "is_bridge", "bridge_ids", "bridges", "bridge", "_built",
    )

    def __init__(self, n, edges=None):
        assert n >= 0
        self.n = n
        self.graph = [[] for _ in range(n)]
        self.edge_from = []
        self.edge_to = []
        self.order = []
        self.ord = self.order
        self.low = []
        self.parent = []
        self.parent_edge = []
        self.is_articulation = []
        self.articulation = []
        self.is_bridge = []
        self.bridge_ids = []
        self.bridges = []
        self.bridge = self.bridges
        self._built = False
        if edges is not None:
            for u, v in edges:
                self.add_edge(u, v)
            self.build()

    def add_edge(self, u, v):
        assert not self._built
        assert 0 <= u < self.n and 0 <= v < self.n
        edge_id = len(self.edge_from)
        self.edge_from.append(u)
        self.edge_to.append(v)
        self.graph[u].append(edge_id)
        self.graph[v].append(edge_id)
        return edge_id

    def get_edge(self, edge_id):
        return self.edge_from[edge_id], self.edge_to[edge_id]

    def build(self):
        if self._built:
            return self
        self._built = True
        n = self.n
        graph = self.graph
        edge_from = self.edge_from
        edge_to = self.edge_to
        order = [-1] * n
        low = [-1] * n
        parent = [-1] * n
        parent_edge = [-1] * n
        current = [0] * n
        child_count = [0] * n
        is_articulation = [False] * n
        is_bridge = [False] * len(edge_from)
        bridge_ids = []
        timer = 0

        for root in range(n):
            if order[root] != -1:
                continue
            order[root] = low[root] = timer
            timer += 1
            stack = [root]
            while stack:
                v = stack[-1]
                i = current[v]
                if i < len(graph[v]):
                    edge_id = graph[v][i]
                    current[v] = i + 1
                    if edge_id == parent_edge[v]:
                        continue
                    to = edge_from[edge_id] ^ edge_to[edge_id] ^ v
                    if order[to] == -1:
                        parent[to] = v
                        parent_edge[to] = edge_id
                        child_count[v] += 1
                        order[to] = low[to] = timer
                        timer += 1
                        stack.append(to)
                    elif order[to] < low[v]:
                        low[v] = order[to]
                    continue

                stack.pop()
                p = parent[v]
                if p == -1:
                    if child_count[v] >= 2:
                        is_articulation[v] = True
                    continue
                if low[v] < low[p]:
                    low[p] = low[v]
                if low[v] > order[p]:
                    edge_id = parent_edge[v]
                    is_bridge[edge_id] = True
                    bridge_ids.append(edge_id)
                if parent[p] != -1 and low[v] >= order[p]:
                    is_articulation[p] = True

        bridges = []
        for edge_id in bridge_ids:
            u = edge_from[edge_id]
            v = edge_to[edge_id]
            bridges.append((u, v) if u < v else (v, u))
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
        return self

    run = build


def lowlink(n, edges):
    return LowLink(n, edges)
