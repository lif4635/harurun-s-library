"""木のEuler tour順と部分木区間を構築する。"""

from library_codex.range_query.StaticRMQ import StaticRMQ

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

