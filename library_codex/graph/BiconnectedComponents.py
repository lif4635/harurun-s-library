from library_codex.graph.LowLink import LowLink


class BiconnectedComponents:
    __slots__ = (
        "lowlink", "edge_components", "vertex_components", "component_of_edge"
    )

    def __init__(self, vertex_count, edges=None):
        if isinstance(vertex_count, LowLink):
            lowlink = vertex_count.build()
        else:
            lowlink = LowLink(vertex_count, edges)
        n = lowlink.n
        graph = lowlink.graph
        edge_from = lowlink.edge_from
        edge_to = lowlink.edge_to
        order = lowlink.order
        low = lowlink.low
        parent_edge = lowlink.parent_edge
        edge_components = []
        component_of_edge = [-1] * len(edge_from)
        self_loops = [[] for _ in range(n)]
        for edge_id, (first, second) in enumerate(zip(edge_from, edge_to)):
            if first == second:
                self_loops[first].append(edge_id)
        for node in range(n):
            for edge_id in self_loops[node]:
                component_of_edge[edge_id] = len(edge_components)
                edge_components.append([edge_id])

        used = bytearray(n)
        for root in range(n):
            if used[root]:
                continue
            used[root] = 1
            edge_stack = []
            stack = [(root, 0)]
            while stack:
                node, index = stack[-1]
                if index == len(graph[node]):
                    stack.pop()
                    edge_id = parent_edge[node]
                    if edge_id >= 0:
                        parent = edge_from[edge_id] ^ edge_to[edge_id] ^ node
                        if low[node] >= order[parent]:
                            component = []
                            while edge_stack:
                                current = edge_stack.pop()
                                component.append(current)
                                if current == edge_id:
                                    break
                            component_id = len(edge_components)
                            for current in component:
                                component_of_edge[current] = component_id
                            edge_components.append(component)
                    continue
                edge_id = graph[node][index]
                stack[-1] = (node, index + 1)
                first = edge_from[edge_id]
                second = edge_to[edge_id]
                if first == second or edge_id == parent_edge[node]:
                    continue
                other = first ^ second ^ node
                if parent_edge[other] == edge_id:
                    edge_stack.append(edge_id)
                    used[other] = 1
                    stack.append((other, 0))
                elif order[other] < order[node]:
                    edge_stack.append(edge_id)
            if edge_stack:
                component_id = len(edge_components)
                component = edge_stack[:]
                for edge_id in component:
                    component_of_edge[edge_id] = component_id
                edge_components.append(component)
                edge_stack.clear()

        vertex_components = []
        appeared = bytearray(n)
        for component in edge_components:
            vertices = []
            for edge_id in component:
                first = edge_from[edge_id]
                second = edge_to[edge_id]
                if not appeared[first]:
                    appeared[first] = 1
                    vertices.append(first)
                if not appeared[second]:
                    appeared[second] = 1
                    vertices.append(second)
            for vertex in vertices:
                appeared[vertex] = 0
            vertex_components.append(vertices)
        incident = [0] * n
        for vertices in vertex_components:
            for vertex in vertices:
                incident[vertex] += 1
        for vertex in range(n):
            if incident[vertex] == 0:
                vertex_components.append([vertex])
                edge_components.append([])
        self.lowlink = lowlink
        self.edge_components = edge_components
        self.vertex_components = vertex_components
        self.component_of_edge = component_of_edge

    @property
    def components(self):
        return self.vertex_components

    @property
    def bc(self):
        lowlink = self.lowlink
        return [
            [lowlink.get_edge(edge_id) for edge_id in component]
            for component in self.edge_components
        ]


class BlockCutTree:
    __slots__ = (
        "biconnected", "tree", "articulation_count", "articulation_id",
        "block_id", "vertex_id"
    )

    def __init__(self, vertex_count, edges=None):
        biconnected = (
            vertex_count
            if isinstance(vertex_count, BiconnectedComponents)
            else BiconnectedComponents(vertex_count, edges)
        )
        lowlink = biconnected.lowlink
        articulation = lowlink.articulation
        articulation_id = [-1] * lowlink.n
        for index, vertex in enumerate(articulation):
            articulation_id[vertex] = index
        articulation_count = len(articulation)
        block_id = [
            articulation_count + index
            for index in range(len(biconnected.vertex_components))
        ]
        tree = [[] for _ in range(articulation_count + len(block_id))]
        vertex_id = [-1] * lowlink.n
        for index, vertices in enumerate(biconnected.vertex_components):
            block = block_id[index]
            for vertex in vertices:
                articulation_node = articulation_id[vertex]
                if articulation_node >= 0:
                    tree[block].append(articulation_node)
                    tree[articulation_node].append(block)
                else:
                    vertex_id[vertex] = block
        for vertex in articulation:
            vertex_id[vertex] = articulation_id[vertex]
        self.biconnected = biconnected
        self.tree = tree
        self.articulation_count = articulation_count
        self.articulation_id = articulation_id
        self.block_id = block_id
        self.vertex_id = vertex_id

    def id(self, vertex):
        return self.vertex_id[vertex]

    def is_articulation(self, vertex):
        return self.articulation_id[vertex] >= 0

    is_arti = is_articulation

    def __len__(self):
        return len(self.tree)

    def __getitem__(self, node):
        return self.tree[node]


BiConnectedComponents = BiconnectedComponents
