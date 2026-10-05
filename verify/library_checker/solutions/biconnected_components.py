class LowLink:
    __slots__ = ('n', 'graph', 'edge_from', 'edge_to', 'order', 'ord', 'low', 'parent', 'parent_edge', 'is_articulation', 'articulation', 'is_bridge', 'bridge_ids', 'bridges', 'bridge', '_built')

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
            for (u, v) in edges:
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
        return (self.edge_from[edge_id], self.edge_to[edge_id])

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

class BiconnectedComponents:
    __slots__ = ('lowlink', 'edge_components', 'vertex_components', 'component_of_edge')

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
        for (edge_id, (first, second)) in enumerate(zip(edge_from, edge_to)):
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
                (node, index) = stack[-1]
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
        return [[lowlink.get_edge(edge_id) for edge_id in component] for component in self.edge_components]

class BlockCutTree:
    __slots__ = ('biconnected', 'tree', 'articulation_count', 'articulation_id', 'block_id', 'vertex_id')

    def __init__(self, vertex_count, edges=None):
        biconnected = vertex_count if isinstance(vertex_count, BiconnectedComponents) else BiconnectedComponents(vertex_count, edges)
        lowlink = biconnected.lowlink
        articulation = lowlink.articulation
        articulation_id = [-1] * lowlink.n
        for (index, vertex) in enumerate(articulation):
            articulation_id[vertex] = index
        articulation_count = len(articulation)
        block_id = [articulation_count + index for index in range(len(biconnected.vertex_components))]
        tree = [[] for _ in range(articulation_count + len(block_id))]
        vertex_id = [-1] * lowlink.n
        for (index, vertices) in enumerate(biconnected.vertex_components):
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
import sys

def main():
    read = sys.stdin.buffer.readline
    (n, m) = map(int, read().split())
    edges = [tuple(map(int, read().split())) for _ in range(m)]
    groups = BiconnectedComponents(n, edges).components
    answer = [str(len(groups))]
    answer.extend((str(len(group)) + ' ' + ' '.join(map(str, group)) for group in groups))
    sys.stdout.write('\n'.join(answer))
if __name__ == '__main__':
    main()
