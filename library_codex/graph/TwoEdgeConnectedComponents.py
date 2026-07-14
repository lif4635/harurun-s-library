from library_codex.graph.LowLink import LowLink


class TwoEdgeConnectedComponents:
    __slots__ = (
        "n", "lowlink", "component", "comp", "groups", "tree",
        "edge_mapping", "num_components", "_built",
    )

    def __init__(self, n, edges=None):
        assert n >= 0
        self.n = n
        self.lowlink = LowLink(n)
        self.component = []
        self.comp = self.component
        self.groups = []
        self.tree = []
        self.edge_mapping = []
        self.num_components = 0
        self._built = False
        if edges is not None:
            for u, v in edges:
                self.add_edge(u, v)
            self.build()

    def add_edge(self, u, v):
        assert not self._built
        return self.lowlink.add_edge(u, v)

    def build(self):
        if self._built:
            return self
        self._built = True
        lowlink = self.lowlink.build()
        n = self.n
        graph = lowlink.graph
        edge_from = lowlink.edge_from
        edge_to = lowlink.edge_to
        is_bridge = lowlink.is_bridge
        component = [-1] * n
        groups = []

        for root in range(n):
            if component[root] != -1:
                continue
            cid = len(groups)
            component[root] = cid
            group = []
            stack = [root]
            while stack:
                v = stack.pop()
                group.append(v)
                for edge_id in graph[v]:
                    if is_bridge[edge_id]:
                        continue
                    to = edge_from[edge_id] ^ edge_to[edge_id] ^ v
                    if component[to] == -1:
                        component[to] = cid
                        stack.append(to)
            groups.append(group)

        num_components = len(groups)
        tree = [[] for _ in range(num_components)]
        for edge_id in lowlink.bridge_ids:
            u = component[edge_from[edge_id]]
            v = component[edge_to[edge_id]]
            tree[u].append(v)
            tree[v].append(u)
        edge_mapping = [-1] * len(edge_from)
        for edge_id in range(len(edge_from)):
            if not is_bridge[edge_id]:
                edge_mapping[edge_id] = component[edge_from[edge_id]]

        self.component = component
        self.comp = component
        self.groups = groups
        self.tree = tree
        self.edge_mapping = edge_mapping
        self.num_components = num_components
        return self

    run = build

    def __getitem__(self, vertex):
        return self.component[vertex]

    def get_components(self):
        return self.groups

    get_tecc_vertices = get_components

    def get_edge_mapping(self):
        return self.edge_mapping

    def bridge_forest(self, with_edge_ids=False):
        if not with_edge_ids:
            return self.tree
        forest = [[] for _ in range(self.num_components)]
        component = self.component
        lowlink = self.lowlink
        for edge_id in lowlink.bridge_ids:
            u = component[lowlink.edge_from[edge_id]]
            v = component[lowlink.edge_to[edge_id]]
            forest[u].append((v, edge_id))
            forest[v].append((u, edge_id))
        return forest


def two_edge_connected_components(n, edges):
    return TwoEdgeConnectedComponents(n, edges)
