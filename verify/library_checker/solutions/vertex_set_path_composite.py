class HeavyLightDecomposition:
    __slots__ = ('n', 'parent', 'depth', 'size', 'head', 'tin', 'tout', 'rev')

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
            (u, h) = stack.pop()
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
        return (self.tin[v] + edge, self.tout[v])

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
            (l, r) = (tin[v] + edge, tin[u] + 1)
        else:
            (l, r) = (tin[u] + edge, tin[v] + 1)
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
            (l, r) = (tin[v] + edge, tin[u] + 1)
            if l < r:
                up.append((l, r, True))
        else:
            (l, r) = (tin[u] + edge, tin[v] + 1)
            if l < r:
                down.append((l, r, False))
        up.extend(reversed(down))
        return up

    def index(self, v):
        return self.tin[v]

    def vertex(self, i):
        return self.rev[i]
HLD = HeavyLightDecomposition
'Point updates and range products for an arbitrary monoid.\n\nUse this when values change one position at a time and a half-open interval\nmust be folded with an associative operation.  ``max_right`` and ``min_left``\nalso find the first boundary where a monotone predicate stops holding.\n'

class SegTree:
    __slots__ = ('n', 'size', 'log', 'data', 'op', 'identity')

    def __init__(self, op, identity, values):
        if isinstance(values, int):
            n = values
            values = [identity] * n
        else:
            values = list(values)
            n = len(values)
        size = 1 << (n - 1).bit_length() if n else 1
        data = [identity] * (size << 1)
        data[size:size + n] = values
        for node in range(size - 1, 0, -1):
            data[node] = op(data[node << 1], data[node << 1 | 1])
        self.n = n
        self.size = size
        self.log = size.bit_length() - 1
        self.data = data
        self.op = op
        self.identity = identity

    def set(self, index, value):
        node = index + self.size
        data = self.data
        data[node] = value
        op = self.op
        node >>= 1
        while node:
            data[node] = op(data[node << 1], data[node << 1 | 1])
            node >>= 1

    def add(self, index, value):
        """indexの現在値をop(value, current)で置き換える。O(log N)。"""
        node = index + self.size
        data = self.data
        op = self.op
        data[node] = op(value, data[node])
        node >>= 1
        while node:
            data[node] = op(data[node << 1], data[node << 1 | 1])
            node >>= 1

    def get(self, index):
        return self.data[index + self.size]

    def tolist(self):
        """現在の要素列をlistで返す。O(N)。"""
        return self.data[self.size:self.size + self.n]

    def __str__(self):
        return str(self.tolist())

    def __repr__(self):
        return 'SegTree(%r)' % self.tolist()

    def prod(self, left, right):
        left += self.size
        right += self.size
        first = self.identity
        second = self.identity
        data = self.data
        op = self.op
        while left < right:
            if left & 1:
                first = op(first, data[left])
                left += 1
            if right & 1:
                right -= 1
                second = op(data[right], second)
            left >>= 1
            right >>= 1
        return op(first, second)
    query = prod

    def all_prod(self):
        return self.data[1]

    def max_right(self, left, predicate):
        if left == self.n:
            return self.n
        left += self.size
        value = self.identity
        data = self.data
        op = self.op
        while True:
            while not left & 1:
                left >>= 1
            merged = op(value, data[left])
            if not predicate(merged):
                while left < self.size:
                    left <<= 1
                    merged = op(value, data[left])
                    if predicate(merged):
                        value = merged
                        left += 1
                return min(left - self.size, self.n)
            value = merged
            left += 1
            if left & -left == left:
                break
        return self.n

    def min_left(self, right, predicate):
        if right == 0:
            return 0
        right += self.size
        value = self.identity
        data = self.data
        op = self.op
        while True:
            right -= 1
            while right > 1 and right & 1:
                right >>= 1
            merged = op(data[right], value)
            if not predicate(merged):
                while right < self.size:
                    right = right << 1 | 1
                    merged = op(data[right], value)
                    if predicate(merged):
                        value = merged
                        right -= 1
                return max(0, right + 1 - self.size)
            value = merged
            if right & -right == right:
                break
        return 0

    def __getitem__(self, index):
        return self.get(index)
import sys

def compose(first, second):
    (a, b) = first
    (c, d) = second
    return (a * c % 998244353, (b * c + d) % 998244353)

def solve():
    data = iter(map(int, sys.stdin.buffer.read().split()))
    (n, q) = (next(data), next(data))
    values = [(next(data), next(data)) for _ in range(n)]
    graph = [[] for _ in range(n)]
    for _ in range(n - 1):
        (u, v) = (next(data), next(data))
        graph[u].append(v)
        graph[v].append(u)
    tree = HeavyLightDecomposition(graph)
    ordered = [values[v] for v in tree.rev]
    forward = SegTree(compose, (1, 0), ordered)
    backward = SegTree(compose, (1, 0), ordered[::-1])
    answer = []
    for _ in range(q):
        if next(data) == 0:
            (p, a, b) = (next(data), next(data), next(data))
            i = tree.tin[p]
            forward.set(i, (a, b))
            backward.set(n - 1 - i, (a, b))
        else:
            (u, v, x) = (next(data), next(data), next(data))
            for (l, r, reverse) in tree.path_ordered(u, v):
                (a, b) = backward.prod(n - r, n - l) if reverse else forward.prod(l, r)
                x = (a * x + b) % 998244353
            answer.append(str(x))
    print('\n'.join(answer))
if __name__ == '__main__':
    solve()
