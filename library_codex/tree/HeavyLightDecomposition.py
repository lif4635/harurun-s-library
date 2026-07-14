class HeavyLightDecomposition:
    __slots__ = ("n", "parent", "depth", "size", "head", "tin", "tout", "rev")

    def __init__(self, edge, root=0):
        n = len(edge)
        assert 0 <= root < n

        parent = [-1] * n
        depth = [0] * n
        order = [root]
        for u in order:
            for v in edge[u]:
                if v != parent[u]:
                    parent[v] = u
                    depth[v] = depth[u] + 1
                    order.append(v)

        size = [1] * n
        heavy = [-1] * n
        for u in reversed(order):
            best = 0
            for v in edge[u]:
                if parent[v] == u:
                    sv = size[v]
                    size[u] += sv
                    if sv > best:
                        best = sv
                        heavy[u] = v

        head = [0] * n
        tin = [0] * n
        rev = [0] * n
        stack = [(root, root)]
        timer = 0
        while stack:
            u, h = stack.pop()
            while u != -1:
                head[u] = h
                tin[u] = timer
                rev[timer] = u
                timer += 1
                hu = heavy[u]
                for v in edge[u]:
                    if parent[v] == u and v != hu:
                        stack.append((v, v))
                u = hu

        self.n = n
        self.parent = parent
        self.depth = depth
        self.size = size
        self.head = head
        self.tin = tin
        self.tout = [tin[v] + size[v] for v in range(n)]
        self.rev = rev

    def lca(self, u, v):
        parent = self.parent
        depth = self.depth
        head = self.head
        while head[u] != head[v]:
            if depth[head[u]] > depth[head[v]]:
                u = parent[head[u]]
            else:
                v = parent[head[v]]
        return u if depth[u] < depth[v] else v

    def dist(self, u, v):
        w = self.lca(u, v)
        return self.depth[u] + self.depth[v] - (self.depth[w] << 1)

    def kth_ancestor(self, v, k):
        if k < 0 or self.depth[v] < k:
            return -1
        parent = self.parent
        depth = self.depth
        head = self.head
        tin = self.tin
        while depth[v] - depth[head[v]] < k:
            k -= depth[v] - depth[head[v]] + 1
            v = parent[head[v]]
        return self.rev[tin[v] - k]

    def jump(self, u, v, k):
        w = self.lca(u, v)
        up = self.depth[u] - self.depth[w]
        distance = up + self.depth[v] - self.depth[w]
        if k < 0 or distance < k:
            return -1
        if k <= up:
            return self.kth_ancestor(u, k)
        return self.kth_ancestor(v, distance - k)

    def next_on_path(self, u, v):
        if u == v:
            return -1
        return self.jump(u, v, 1)

    nxt = next_on_path

    def vertices_on_path(self, u, v):
        distance = self.dist(u, v)
        return [self.jump(u, v, k) for k in range(distance + 1)]

    def subtree(self, v, edge=False):
        return self.tin[v] + edge, self.tout[v]

    def path(self, u, v, edge=False):
        res = []
        parent = self.parent
        depth = self.depth
        head = self.head
        tin = self.tin
        while head[u] != head[v]:
            if depth[head[u]] > depth[head[v]]:
                res.append((tin[head[u]], tin[u] + 1))
                u = parent[head[u]]
            else:
                res.append((tin[head[v]], tin[v] + 1))
                v = parent[head[v]]
        if depth[u] > depth[v]:
            l, r = tin[v] + edge, tin[u] + 1
        else:
            l, r = tin[u] + edge, tin[v] + 1
        if l < r:
            res.append((l, r))
        return res

    def path_ordered(self, u, v, edge=False):
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
            l, r = tin[v] + edge, tin[u] + 1
            if l < r:
                up.append((l, r, True))
        else:
            l, r = tin[u] + edge, tin[v] + 1
            if l < r:
                down.append((l, r, False))
        up.extend(reversed(down))
        return up

    def index(self, v):
        return self.tin[v]

    def vertex(self, i):
        return self.rev[i]


HLD = HeavyLightDecomposition
