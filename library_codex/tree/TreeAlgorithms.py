from library_codex.data_structure.StaticRMQ import StaticRMQ
from library_codex.tree.HeavyLightDecomposition import HeavyLightDecomposition


def _edge(entry):
    if isinstance(entry, int):
        return entry, 1
    return entry[0], entry[1]


class EulerTour:
    __slots__ = (
        "n",
        "down",
        "up",
        "parent",
        "depth",
        "component",
        "tour",
        "tour_depth",
        "rmq",
    )

    def __init__(self, tree, root=0):
        n = len(tree)
        if n == 0:
            self.n = 0
            self.down = []
            self.up = []
            self.parent = []
            self.depth = []
            self.component = []
            self.tour = []
            self.tour_depth = []
            self.rmq = None
            return
        if not 0 <= root < n:
            raise IndexError("root is out of range")
        down = [-1] * n
        up = [-1] * n
        parent = [-2] * n
        depth = [0] * n
        component = [-1] * n
        tour = []
        tour_depth = []
        starts = [root]
        starts.extend(node for node in range(n) if node != root)
        component_id = 0
        for start in starts:
            if parent[start] != -2:
                continue
            parent[start] = -1
            component[start] = component_id
            down[start] = len(tour)
            tour.append(start)
            tour_depth.append(0)
            stack = [[start, -1, 0]]
            while stack:
                node, par, index = stack[-1]
                if index == len(tree[node]):
                    up[node] = len(tour)
                    stack.pop()
                    if par >= 0:
                        tour.append(par)
                        tour_depth.append(depth[par])
                    continue
                entry = tree[node][index]
                stack[-1][2] = index + 1
                other, _ = _edge(entry)
                if other == par:
                    continue
                if not 0 <= other < n or parent[other] != -2:
                    raise ValueError("graph must be a forest")
                parent[other] = node
                depth[other] = depth[node] + 1
                component[other] = component_id
                down[other] = len(tour)
                tour.append(other)
                tour_depth.append(depth[other])
                stack.append([other, node, 0])
            component_id += 1
        self.n = n
        self.down = down
        self.up = up
        self.parent = parent
        self.depth = depth
        self.component = component
        self.tour = tour
        self.tour_depth = tour_depth
        self.rmq = StaticRMQ(
            [(tour_depth[index], tour[index]) for index in range(len(tour))]
        )

    def idx(self, node):
        return self.down[node], self.up[node]

    def lca(self, first, second):
        if self.component[first] != self.component[second]:
            return -1
        left = self.down[first]
        right = self.down[second]
        if left > right:
            left, right = right, left
        return self.rmq.query(left, right + 1)[1]

    def distance(self, first, second):
        ancestor = self.lca(first, second)
        if ancestor < 0:
            return -1
        return (
            self.depth[first]
            + self.depth[second]
            - (self.depth[ancestor] << 1)
        )

    dist = distance

    def node_intervals(self, first, second):
        ancestor = self.lca(first, second)
        if ancestor < 0:
            return []
        return [
            (self.down[ancestor], self.down[first] + 1),
            (self.down[ancestor] + 1, self.down[second] + 1),
        ]

    node_query = node_intervals

    def edge_intervals(self, first, second):
        ancestor = self.lca(first, second)
        if ancestor < 0:
            return []
        left = self.down[ancestor] + 1
        return [(left, self.down[first] + 1), (left, self.down[second] + 1)]

    edge_query = edge_intervals

    def subtree_interval(self, node):
        return self.down[node], self.up[node]

    subtree_query = subtree_interval

    def __len__(self):
        return len(self.tour)


class AuxiliaryTree:
    __slots__ = ("tree", "hld")

    def __init__(self, tree, root=0):
        self.tree = tree
        self.hld = HeavyLightDecomposition(tree, root)

    def get(self, vertices, with_distance=False):
        vertices = list(set(vertices))
        if not vertices:
            return ([], [])
        hld = self.hld
        tin = hld.tin
        vertices.sort(key=tin.__getitem__)
        original_size = len(vertices)
        for index in range(original_size - 1):
            vertices.append(hld.lca(vertices[index], vertices[index + 1]))
        vertices = sorted(set(vertices), key=tin.__getitem__)
        index_of = {vertex: index for index, vertex in enumerate(vertices)}
        auxiliary = [[] for _ in vertices]
        stack = [vertices[0]]
        tout = hld.tout
        depth = hld.depth
        for vertex in vertices[1:]:
            while not (tin[stack[-1]] <= tin[vertex] < tout[stack[-1]]):
                stack.pop()
            parent = stack[-1]
            if with_distance:
                auxiliary[index_of[parent]].append(
                    (index_of[vertex], depth[vertex] - depth[parent])
                )
            else:
                auxiliary[index_of[parent]].append(index_of[vertex])
            stack.append(vertex)
        return auxiliary, vertices

    build = get
    query = get


def cartesian_tree(values, minimum=True):
    values = list(values)
    n = len(values)
    parent = [-1] * n
    left = [-1] * n
    right = [-1] * n
    stack = []
    if minimum:
        for index, value in enumerate(values):
            previous = -1
            while stack and value < values[stack[-1]]:
                previous = stack.pop()
            if previous >= 0:
                parent[previous] = index
                left[index] = previous
            if stack:
                parent[index] = stack[-1]
                right[stack[-1]] = index
            stack.append(index)
    else:
        for index, value in enumerate(values):
            previous = -1
            while stack and value > values[stack[-1]]:
                previous = stack.pop()
            if previous >= 0:
                parent[previous] = index
                left[index] = previous
            if stack:
                parent[index] = stack[-1]
                right[stack[-1]] = index
            stack.append(index)
    root = stack[0] if stack else -1
    return parent, left, right, root


def cartesian_tree_graph(values, minimum=True, directed=True):
    parent, left, right, root = cartesian_tree(values, minimum)
    graph = [[] for _ in parent]
    for node, par in enumerate(parent):
        if par >= 0:
            graph[par].append(node)
            if not directed:
                graph[node].append(par)
    return graph, root


def rooted_tree(tree, root=0):
    n = len(tree)
    if n == 0:
        return []
    parent = [-2] * n
    parent[root] = -1
    order = [root]
    result = [[] for _ in range(n)]
    for node in order:
        for entry in tree[node]:
            other, _ = _edge(entry)
            if other == parent[node]:
                continue
            if parent[other] != -2:
                raise ValueError("graph must be a tree")
            parent[other] = node
            result[node].append(entry)
            order.append(other)
    if len(order) != n:
        raise ValueError("graph must be connected")
    return result


def inverse_tree(tree):
    result = [[] for _ in tree]
    for node, row in enumerate(tree):
        for entry in row:
            if isinstance(entry, int):
                result[entry].append(node)
            else:
                result[entry[0]].append((node, *entry[1:]))
    return result


def process_of_merging_tree(edges, size=None, sort_edges=False):
    edges = list(edges)
    if size is None:
        size = 1
        for edge in edges:
            size = max(size, edge[0] + 1, edge[1] + 1)
    if sort_edges:
        edges.sort(key=lambda edge: edge[2])
    parent = list(range(size))
    component_size = [1] * size
    roots = list(range(size))
    graph = [[] for _ in range(max(1, size * 2 - 1))]
    weights = []

    def find(node):
        root = node
        while parent[root] != root:
            root = parent[root]
        while parent[node] != node:
            next_node = parent[node]
            parent[node] = root
            node = next_node
        return root

    auxiliary = size
    for first, second, weight, *_ in edges:
        first = find(first)
        second = find(second)
        if first == second:
            continue
        graph[auxiliary].append((roots[first], weight))
        graph[auxiliary].append((roots[second], weight))
        weights.append(weight)
        if component_size[first] < component_size[second]:
            first, second = second, first
        parent[second] = first
        component_size[first] += component_size[second]
        roots[first] = auxiliary
        auxiliary += 1
    if size and auxiliary != size * 2 - 1:
        raise ValueError("edges do not connect all vertices")
    return graph[:auxiliary], weights, auxiliary - 1


def inclusion_tree(intervals, universe_size=None):
    intervals = list(intervals)
    if universe_size is None:
        universe_size = max((right for _, right in intervals), default=0)
    indexed = [(-1, universe_size + 1, -1)]
    indexed.extend(
        (left, right, index)
        for index, (left, right) in enumerate(intervals)
    )
    indexed[1:] = sorted(indexed[1:], key=lambda item: (item[0], -item[1]))
    graph = [[] for _ in indexed]
    parent = [-1] * len(indexed)
    stack = [0]
    for index in range(1, len(indexed)):
        left, right, _ = indexed[index]
        while stack and indexed[stack[-1]][1] < right:
            previous = stack.pop()
            if left < indexed[previous][1]:
                raise ValueError("intervals cross")
        if not stack or not (
            indexed[stack[-1]][0] <= left
            and right <= indexed[stack[-1]][1]
        ):
            raise ValueError("interval is outside the universe")
        parent[index] = stack[-1]
        graph[stack[-1]].append(index)
        stack.append(index)
    return graph, [(left, right) for left, right, _ in indexed], [
        original for _, _, original in indexed
    ]


def tree_diameter(tree):
    n = len(tree)
    if n == 0:
        return 0, []

    def farthest(start, keep_parent=False):
        parent = [-2] * n
        parent[start] = -1
        distance = [None] * n
        distance[start] = 0
        order = [start]
        best = start
        for node in order:
            value = distance[node]
            if value > distance[best]:
                best = node
            for entry in tree[node]:
                other, weight = _edge(entry)
                if other == parent[node]:
                    continue
                if parent[other] != -2:
                    raise ValueError("graph must be a tree")
                parent[other] = node
                distance[other] = value + weight
                order.append(other)
        if len(order) != n:
            raise ValueError("graph must be connected")
        return best, distance, parent if keep_parent else None

    first, _, _ = farthest(0)
    second, distance, parent = farthest(first, True)
    path = []
    node = second
    while node >= 0:
        path.append(node)
        if node == first:
            break
        node = parent[node]
    return distance[second], path


def diameter(tree):
    return tree_diameter(tree)[0]


diameter_path = tree_diameter
CartesianTree = cartesian_tree_graph
