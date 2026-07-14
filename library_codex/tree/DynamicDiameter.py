from library_codex.tree.StaticTopTree import (
    StaticTopTreeVertexBased,
    VertexTopTreeDP,
)


def _maximum_path(first, second):
    return first if first >= second else second


def _maximum_half(first, second):
    return first if first >= second else second


def _vertex(weight, vertex):
    path = (weight, vertex, vertex)
    half = (weight, vertex)
    return path, half, half, weight, vertex, vertex


def _compress(parent, child):
    parent_diameter, parent_up, parent_down, parent_length, first, _ = parent
    child_diameter, child_up, child_down, child_length, _, last = child
    diameter = _maximum_path(parent_diameter, child_diameter)
    diameter = _maximum_path(
        diameter,
        (
            parent_down[0] + child_up[0],
            parent_down[1],
            child_up[1],
        ),
    )
    up = _maximum_half(
        parent_up,
        (parent_length + child_up[0], child_up[1]),
    )
    down = _maximum_half(
        child_down,
        (child_length + parent_down[0], parent_down[1]),
    )
    return diameter, up, down, parent_length + child_length, first, last


def _rake(first, second):
    diameter = _maximum_path(first[0], second[0])
    halves = [first[1], first[2], second[1], second[2]]
    halves.sort(reverse=True)
    return diameter, halves[0], halves[1]


def _add_edge(path):
    return path[0], path[1], (0, -1)


class DynamicDiameter:
    __slots__ = (
        "n",
        "graph",
        "auxiliary_graph",
        "weights",
        "edge_node",
        "top_tree",
        "dp",
    )

    def __init__(self, tree):
        n = len(tree)
        if n == 0:
            raise ValueError("tree must be nonempty")
        auxiliary_graph = [[] for _ in range(n * 2 - 1)]
        weights = [0] * (n * 2 - 1)
        edge_node = {}
        parent = [-2] * n
        parent[0] = -1
        order = [0]
        next_node = n
        for node in order:
            for entry in tree[node]:
                if isinstance(entry, int):
                    other, weight = entry, 1
                else:
                    other, weight = entry[0], entry[1]
                if other == parent[node]:
                    continue
                if parent[other] != -2:
                    raise ValueError("graph must be a tree")
                parent[other] = node
                order.append(other)
                middle = next_node
                next_node += 1
                auxiliary_graph[node].append(middle)
                auxiliary_graph[middle].append(node)
                auxiliary_graph[other].append(middle)
                auxiliary_graph[middle].append(other)
                weights[middle] = weight
                edge_node[(min(node, other), max(node, other))] = middle
        if len(order) != n or next_node != n * 2 - 1:
            raise ValueError("graph must be connected")
        self.n = n
        self.graph = tree
        self.auxiliary_graph = auxiliary_graph
        self.weights = weights
        self.edge_node = edge_node
        top_tree = StaticTopTreeVertexBased(auxiliary_graph)
        self.top_tree = top_tree

        def vertex(node):
            return _vertex(weights[node], node if node < n else -1)

        def add_vertex(point, node):
            weight = weights[node]
            diameter, first, second = point
            candidate = (
                first[0] + weight + second[0],
                first[1],
                second[1],
            )
            diameter = _maximum_path(diameter, candidate)
            half = (first[0] + weight, first[1])
            vertex_id = node if node < n else -1
            return diameter, half, half, weight, vertex_id, vertex_id

        self.dp = VertexTopTreeDP(
            top_tree,
            vertex,
            _compress,
            _rake,
            _add_edge,
            add_vertex,
        )

    def get(self):
        distance, first, second = self.dp.get()[0]
        return distance, (first, second)

    def update(self, first, second, weight):
        key = (min(first, second), max(first, second))
        node = self.edge_node.get(key)
        if node is None:
            raise KeyError("edge does not exist")
        self.weights[node] = weight
        self.dp.update(node)

    set_edge = update
