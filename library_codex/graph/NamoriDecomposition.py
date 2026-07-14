class NamoriDecomposition:
    __slots__ = (
        "n", "graph", "edge_from", "edge_to", "edge_weight", "components",
        "component_id", "comp", "component_edge_count", "is_cycle_edge",
        "on_cycle", "cycles", "cycle_edge_ids", "cycle_weights",
        "cycle_prefix", "cycle_total", "cycle_of_component", "cycle_id",
        "cycle_position", "roots", "parent", "parent_edge", "depth",
        "distance_to_root", "subtree_size", "head", "tin", "tout", "rev",
        "tree_index", "_built",
    )

    def __init__(self, n, edges=None):
        assert n >= 0
        self.n = n
        self.graph = [[] for _ in range(n)]
        self.edge_from = []
        self.edge_to = []
        self.edge_weight = []
        self.components = []
        self.component_id = []
        self.comp = self.component_id
        self.component_edge_count = []
        self.is_cycle_edge = []
        self.on_cycle = []
        self.cycles = []
        self.cycle_edge_ids = []
        self.cycle_weights = []
        self.cycle_prefix = []
        self.cycle_total = []
        self.cycle_of_component = []
        self.cycle_id = []
        self.cycle_position = []
        self.roots = []
        self.parent = []
        self.parent_edge = []
        self.depth = []
        self.distance_to_root = []
        self.subtree_size = []
        self.head = []
        self.tin = []
        self.tout = []
        self.rev = []
        self.tree_index = []
        self._built = False
        if edges is not None:
            for edge in edges:
                self.add_edge(*edge)
            self.build()

    def add_edge(self, u, v, weight=1):
        assert not self._built
        assert 0 <= u < self.n and 0 <= v < self.n
        edge_id = len(self.edge_from)
        self.edge_from.append(u)
        self.edge_to.append(v)
        self.edge_weight.append(weight)
        self.graph[u].append(edge_id)
        self.graph[v].append(edge_id)
        return edge_id

    def get_edge(self, edge_id):
        return (
            self.edge_from[edge_id],
            self.edge_to[edge_id],
            self.edge_weight[edge_id],
        )

    def build(self):
        if self._built:
            return self
        self._built = True
        n = self.n
        graph = self.graph
        edge_from = self.edge_from
        edge_to = self.edge_to
        edge_weight = self.edge_weight

        component_id = [-1] * n
        components = []
        component_edge_count = []
        for start in range(n):
            if component_id[start] != -1:
                continue
            cid = len(components)
            component_id[start] = cid
            group = []
            degree_sum = 0
            stack = [start]
            while stack:
                v = stack.pop()
                group.append(v)
                degree_sum += len(graph[v])
                for edge_id in graph[v]:
                    to = edge_from[edge_id] ^ edge_to[edge_id] ^ v
                    if component_id[to] == -1:
                        component_id[to] = cid
                        stack.append(to)
            edge_count = degree_sum >> 1
            if edge_count > len(group):
                raise ValueError("each connected component must have at most one cycle")
            components.append(group)
            component_edge_count.append(edge_count)

        degree = [len(edges) for edges in graph]
        removed = [False] * n
        stack = [v for v in range(n) if degree[v] <= 1]
        while stack:
            v = stack.pop()
            if removed[v]:
                continue
            removed[v] = True
            for edge_id in graph[v]:
                to = edge_from[edge_id] ^ edge_to[edge_id] ^ v
                if not removed[to]:
                    degree[to] -= 1
                    if degree[to] == 1:
                        stack.append(to)
        on_cycle = [not value for value in removed]

        cycle_position = [-1] * n
        cycle_of_component = [-1] * len(components)
        is_cycle_edge = [False] * len(edge_from)
        used_cycle = [False] * n
        cycles = []
        cycle_edge_ids = []
        cycle_weights = []
        cycle_prefix = []
        cycle_total = []
        for start in range(n):
            if not on_cycle[start] or used_cycle[start]:
                continue
            cycle = []
            edge_ids = []
            weights = []
            current = start
            previous_edge = -1
            while True:
                if used_cycle[current]:
                    raise ValueError("invalid cycle core")
                used_cycle[current] = True
                cycle_position[current] = len(cycle)
                cycle.append(current)
                next_edge = -1
                next_vertex = -1
                for edge_id in graph[current]:
                    to = edge_from[edge_id] ^ edge_to[edge_id] ^ current
                    if on_cycle[to] and edge_id != previous_edge:
                        next_edge = edge_id
                        next_vertex = to
                        break
                if next_edge == -1:
                    raise ValueError("invalid cycle core")
                edge_ids.append(next_edge)
                weights.append(edge_weight[next_edge])
                is_cycle_edge[next_edge] = True
                if next_vertex == start:
                    break
                previous_edge = next_edge
                current = next_vertex
            cycle_id = len(cycles)
            cycle_of_component[component_id[start]] = cycle_id
            prefix = [0]
            for weight in weights:
                prefix.append(prefix[-1] + weight)
            cycles.append(cycle)
            cycle_edge_ids.append(edge_ids)
            cycle_weights.append(weights)
            cycle_prefix.append(prefix)
            cycle_total.append(prefix[-1])

        cycle_id = [
            cycle_of_component[component_id[v]] for v in range(n)
        ]
        roots = [-1] * n
        parent = [-2] * n
        parent_edge = [-1] * n
        depth = [0] * n
        distance_to_root = [0] * n
        forest_roots = []
        for cycle in cycles:
            for root in cycle:
                roots[root] = root
                parent[root] = -1
                forest_roots.append(root)
        for cid, group in enumerate(components):
            if cycle_of_component[cid] == -1:
                root = group[0]
                roots[root] = root
                parent[root] = -1
                forest_roots.append(root)

        order = forest_roots.copy()
        for v in order:
            for edge_id in graph[v]:
                if is_cycle_edge[edge_id]:
                    continue
                to = edge_from[edge_id] ^ edge_to[edge_id] ^ v
                if parent[to] == -2:
                    parent[to] = v
                    parent_edge[to] = edge_id
                    roots[to] = roots[v]
                    depth[to] = depth[v] + 1
                    distance_to_root[to] = (
                        distance_to_root[v] + edge_weight[edge_id]
                    )
                    order.append(to)
        if len(order) != n:
            raise ValueError("the graph is not a pseudoforest")

        subtree_size = [1] * n
        heavy = [-1] * n
        for v in reversed(order):
            p = parent[v]
            if p != -1:
                subtree_size[p] += subtree_size[v]
                h = heavy[p]
                if h == -1 or subtree_size[v] > subtree_size[h]:
                    heavy[p] = v

        head = [0] * n
        tin = [0] * n
        rev = [0] * n
        hld_stack = [(root, root) for root in reversed(forest_roots)]
        timer = 0
        while hld_stack:
            v, chain_head = hld_stack.pop()
            while v != -1:
                head[v] = chain_head
                tin[v] = timer
                rev[timer] = v
                timer += 1
                heavy_child = heavy[v]
                for edge_id in graph[v]:
                    if is_cycle_edge[edge_id]:
                        continue
                    to = edge_from[edge_id] ^ edge_to[edge_id] ^ v
                    if parent[to] == v and to != heavy_child:
                        hld_stack.append((to, to))
                v = heavy_child

        self.components = components
        self.component_id = component_id
        self.comp = component_id
        self.component_edge_count = component_edge_count
        self.is_cycle_edge = is_cycle_edge
        self.on_cycle = on_cycle
        self.cycles = cycles
        self.cycle_edge_ids = cycle_edge_ids
        self.cycle_weights = cycle_weights
        self.cycle_prefix = cycle_prefix
        self.cycle_total = cycle_total
        self.cycle_of_component = cycle_of_component
        self.cycle_id = cycle_id
        self.cycle_position = cycle_position
        self.roots = roots
        self.parent = parent
        self.parent_edge = parent_edge
        self.depth = depth
        self.distance_to_root = distance_to_root
        self.subtree_size = subtree_size
        self.head = head
        self.tin = tin
        self.tout = [tin[v] + subtree_size[v] for v in range(n)]
        self.rev = rev
        self.tree_index = [tin[v] - tin[roots[v]] for v in range(n)]
        return self

    run = build

    def in_cycle(self, vertex):
        return self.on_cycle[vertex]

    incycle = in_cycle

    def root(self, vertex):
        return self.roots[vertex]

    def component(self, vertex):
        return self.component_id[vertex]

    def same_tree(self, u, v):
        return self.roots[u] == self.roots[v]

    def same_component(self, u, v):
        return self.component_id[u] == self.component_id[v]

    def idx(self, vertex):
        root = self.roots[vertex]
        return self.cycle_position[root], self.tree_index[vertex]

    def lca(self, u, v):
        if self.roots[u] != self.roots[v]:
            return -1
        parent = self.parent
        depth = self.depth
        head = self.head
        while head[u] != head[v]:
            if depth[head[u]] > depth[head[v]]:
                u = parent[head[u]]
            else:
                v = parent[head[v]]
        return u if depth[u] < depth[v] else v

    def tree_hops(self, u, v):
        ancestor = self.lca(u, v)
        if ancestor == -1:
            return None
        return self.depth[u] + self.depth[v] - (self.depth[ancestor] << 1)

    def tree_distance(self, u, v):
        ancestor = self.lca(u, v)
        if ancestor == -1:
            return None
        distance = self.distance_to_root
        return distance[u] + distance[v] - 2 * distance[ancestor]

    def _cycle_distances(self, root_u, root_v, weighted):
        if root_u == root_v:
            return 0, None
        cycle_id = self.cycle_id[root_u]
        if cycle_id == -1 or cycle_id != self.cycle_id[root_v]:
            return None, None
        left = self.cycle_position[root_u]
        right = self.cycle_position[root_v]
        if left > right:
            left, right = right, left
        if weighted:
            first = self.cycle_prefix[cycle_id][right] - self.cycle_prefix[cycle_id][left]
            second = self.cycle_total[cycle_id] - first
        else:
            first = right - left
            second = len(self.cycles[cycle_id]) - first
        if first <= second:
            return first, second
        return second, first

    def distances(self, u, v):
        if self.component_id[u] != self.component_id[v]:
            return None, None
        root_u = self.roots[u]
        root_v = self.roots[v]
        if root_u == root_v:
            return self.tree_distance(u, v), None
        first, second = self._cycle_distances(root_u, root_v, True)
        base = self.distance_to_root[u] + self.distance_to_root[v]
        return base + first, base + second

    dist = distances

    def hop_distances(self, u, v):
        if self.component_id[u] != self.component_id[v]:
            return None, None
        root_u = self.roots[u]
        root_v = self.roots[v]
        if root_u == root_v:
            return self.tree_hops(u, v), None
        first, second = self._cycle_distances(root_u, root_v, False)
        base = self.depth[u] + self.depth[v]
        return base + first, base + second

    def distance(self, u, v):
        return self.distances(u, v)[0]

    def kth_ancestor(self, vertex, k):
        if k < 0 or self.depth[vertex] < k:
            return -1
        parent = self.parent
        depth = self.depth
        head = self.head
        tin = self.tin
        while depth[vertex] - depth[head[vertex]] < k:
            k -= depth[vertex] - depth[head[vertex]] + 1
            vertex = parent[head[vertex]]
        return self.rev[tin[vertex] - k]

    def jump_tree(self, u, v, k):
        ancestor = self.lca(u, v)
        if ancestor == -1:
            return -1
        up = self.depth[u] - self.depth[ancestor]
        distance = up + self.depth[v] - self.depth[ancestor]
        if k < 0 or k > distance:
            return -1
        if k <= up:
            return self.kth_ancestor(u, k)
        return self.kth_ancestor(v, distance - k)

    def path(self, u, v, edge=False):
        if self.roots[u] != self.roots[v]:
            return None
        result = []
        parent = self.parent
        depth = self.depth
        head = self.head
        tin = self.tin
        while head[u] != head[v]:
            if depth[head[u]] > depth[head[v]]:
                result.append((tin[head[u]], tin[u] + 1))
                u = parent[head[u]]
            else:
                result.append((tin[head[v]], tin[v] + 1))
                v = parent[head[v]]
        if depth[u] > depth[v]:
            left, right = tin[v] + edge, tin[u] + 1
        else:
            left, right = tin[u] + edge, tin[v] + 1
        if left < right:
            result.append((left, right))
        return result

    def path_ordered(self, u, v, edge=False):
        if self.roots[u] != self.roots[v]:
            return None
        up = []
        down = []
        parent = self.parent
        depth = self.depth
        head = self.head
        tin = self.tin
        while head[u] != head[v]:
            if depth[head[u]] > depth[head[v]]:
                up.append((tin[head[u]], tin[u] + 1, True))
                u = parent[head[u]]
            else:
                down.append((tin[head[v]], tin[v] + 1, False))
                v = parent[head[v]]
        if depth[u] > depth[v]:
            left, right = tin[v] + edge, tin[u] + 1
            if left < right:
                up.append((left, right, True))
        else:
            left, right = tin[u] + edge, tin[v] + 1
            if left < right:
                down.append((left, right, False))
        up.extend(reversed(down))
        return up

    def subtree(self, vertex, edge=False):
        return self.tin[vertex] + edge, self.tout[vertex]

    def index(self, vertex):
        return self.tin[vertex]

    def vertex(self, index):
        return self.rev[index]


Namori = NamoriDecomposition
NamoriForest = NamoriDecomposition
