class Rerooting:
    """Iterative all-direction tree DP.

    ``put_edge(value, source, target, edge_data)`` converts a completed
    vertex DP into a contribution across one edge.  ``put_vertex(merged,
    vertex)`` adds the vertex itself.  The order passed to ``merge`` follows
    the adjacency-list order.
    """

    __slots__ = (
        "tree",
        "n",
        "merge",
        "identity",
        "put_edge",
        "put_vertex",
        "root",
        "parent",
        "parent_edge",
        "order",
        "down",
        "up",
        "answer",
        "directed_side",
    )

    def __init__(
        self,
        tree,
        merge,
        identity,
        put_edge,
        put_vertex,
        root=0,
    ):
        self.tree = tree
        self.n = len(tree)
        self.merge = merge
        self.identity = identity
        self.put_edge = put_edge
        self.put_vertex = put_vertex
        self.root = root
        self.parent = []
        self.parent_edge = []
        self.order = []
        self.down = []
        self.up = []
        self.answer = []
        self.directed_side = {}
        self.solve()

    def _identity(self):
        identity = self.identity
        return identity() if callable(identity) else identity

    @staticmethod
    def _edge(entry):
        if isinstance(entry, int):
            return entry, None
        return entry[0], entry[1]

    def solve(self):
        n = self.n
        if n == 0:
            self.parent = []
            self.parent_edge = []
            self.order = []
            self.down = []
            self.up = []
            self.answer = []
            self.directed_side = {}
            return []
        root = self.root
        if not 0 <= root < n:
            raise IndexError("root is out of range")
        tree = self.tree
        parent = [-2] * n
        parent_edge = [None] * n
        parent[root] = -1
        order = [root]
        for node in order:
            for entry in tree[node]:
                other, data = self._edge(entry)
                if other == parent[node]:
                    continue
                if not 0 <= other < n or parent[other] != -2:
                    raise ValueError("graph must be a tree")
                parent[other] = node
                parent_edge[other] = data
                order.append(other)
        if len(order) != n:
            raise ValueError("graph must be connected")

        merge = self.merge
        put_edge = self.put_edge
        put_vertex = self.put_vertex
        down = [None] * n
        for node in reversed(order):
            value = self._identity()
            for entry in tree[node]:
                other, data = self._edge(entry)
                if parent[other] == node:
                    value = merge(
                        value,
                        put_edge(down[other], other, node, data),
                    )
            down[node] = put_vertex(value, node)

        up = [None] * n
        up[root] = self._identity()
        answer = [None] * n
        directed_side = {}
        for node in order:
            degree = len(tree[node])
            contributions = [None] * degree
            for index, entry in enumerate(tree[node]):
                other, data = self._edge(entry)
                if other == parent[node]:
                    contributions[index] = up[node]
                else:
                    contributions[index] = put_edge(
                        down[other], other, node, data
                    )
            prefix = [None] * (degree + 1)
            suffix = [None] * (degree + 1)
            prefix[0] = self._identity()
            for index in range(degree):
                prefix[index + 1] = merge(
                    prefix[index], contributions[index]
                )
            suffix[degree] = self._identity()
            for index in range(degree - 1, -1, -1):
                suffix[index] = merge(
                    contributions[index], suffix[index + 1]
                )
            answer[node] = put_vertex(prefix[degree], node)
            for index, entry in enumerate(tree[node]):
                other, data = self._edge(entry)
                if parent[other] != node:
                    continue
                without = merge(prefix[index], suffix[index + 1])
                source_value = put_vertex(without, node)
                directed_side[(node, other)] = source_value
                directed_side[(other, node)] = down[other]
                up[other] = put_edge(
                    source_value, node, other, data
                )
        self.parent = parent
        self.parent_edge = parent_edge
        self.order = order
        self.down = down
        self.up = up
        self.answer = answer
        self.directed_side = directed_side
        return answer

    run = solve

    def __getitem__(self, vertex):
        return self.answer[vertex]

    def edge_side(self, endpoint, other):
        return self.directed_side[(endpoint, other)]


def rerooting_dp(
    tree,
    merge,
    identity,
    put_edge,
    put_vertex,
    root=0,
):
    return Rerooting(
        tree, merge, identity, put_edge, put_vertex, root
    ).answer
