"""Offline path queries on a static tree with Mo's algorithm."""


class TreeMo:
    """Move an active vertex set between tree paths and answer offline queries."""

    __slots__ = (
        "n", "tree", "parent", "depth", "up", "tour", "tin", "tout",
        "queries", "block_size",
    )

    def __init__(self, tree, root=0, query_count=0, block_size=None):
        n = len(tree)
        if not 0 <= root < n:
            raise IndexError("root is out of range")
        parent = [-2] * n
        depth = [0] * n
        tin = [0] * n
        tout = [0] * n
        tour = []
        parent[root] = -1
        stack = [(root, -1, 0)]
        while stack:
            vertex, par, phase = stack.pop()
            if phase == 0:
                tin[vertex] = len(tour)
                tour.append(vertex)
                stack.append((vertex, par, 1))
                for other in reversed(tree[vertex]):
                    if other == par:
                        continue
                    if parent[other] != -2:
                        raise ValueError("graph must be a tree")
                    parent[other] = vertex
                    depth[other] = depth[vertex] + 1
                    stack.append((other, vertex, 0))
            else:
                tout[vertex] = len(tour)
                tour.append(vertex)
        if len(tour) != 2 * n:
            raise ValueError("graph must be connected")
        up = [parent]
        while (1 << len(up)) <= n:
            previous = up[-1]
            up.append([previous[v] if previous[v] < 0 else previous[previous[v]] for v in range(n)])
        self.n = n
        self.tree = tree
        self.parent = parent
        self.depth = depth
        self.up = up
        self.tour = tour
        self.tin = tin
        self.tout = tout
        self.queries = []
        self.block_size = block_size or max(1, int(2 * n / max(1, query_count) ** 0.5))

    def lca(self, first, second):
        if self.depth[first] < self.depth[second]:
            first, second = second, first
        difference = self.depth[first] - self.depth[second]
        bit = 0
        while difference:
            if difference & 1:
                first = self.up[bit][first]
            difference >>= 1
            bit += 1
        if first == second:
            return first
        for row in reversed(self.up):
            if row[first] != row[second]:
                first = row[first]
                second = row[second]
        return self.parent[first]

    def add_query(self, first, second):
        if self.tin[first] > self.tin[second]:
            first, second = second, first
        ancestor = self.lca(first, second)
        if ancestor == first:
            left, right, extra = self.tin[first], self.tin[second] + 1, -1
        else:
            left, right, extra = self.tout[first], self.tin[second] + 1, ancestor
        self.queries.append((left, right, extra, len(self.queries)))
        return len(self.queries) - 1

    def order(self):
        width = self.block_size
        return sorted(
            self.queries,
            key=lambda query: (
                query[0] // width,
                query[1] if (query[0] // width) & 1 == 0 else -query[1],
            ),
        )

    def run(self, add, remove, get):
        """Return answers; callbacks receive vertices entering/leaving the path."""
        answer = [None] * len(self.queries)
        active = bytearray(self.n)
        tour = self.tour

        def toggle(position):
            vertex = tour[position]
            if active[vertex]:
                active[vertex] = 0
                remove(vertex)
            else:
                active[vertex] = 1
                add(vertex)

        left = right = 0
        for query_left, query_right, extra, query_id in self.order():
            while query_left < left:
                left -= 1
                toggle(left)
            while right < query_right:
                toggle(right)
                right += 1
            while left < query_left:
                toggle(left)
                left += 1
            while query_right < right:
                right -= 1
                toggle(right)
            if extra >= 0:
                add(extra)
            answer[query_id] = get()
            if extra >= 0:
                remove(extra)
        return answer
