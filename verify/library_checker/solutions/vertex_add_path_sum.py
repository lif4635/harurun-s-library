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
'一点加算・prefix和・区間和を対数時間で扱うBIT。'

class BIT:
    __slots__ = ('n', 'bit')

    def __init__(self, values):
        if isinstance(values, int):
            if values < 0:
                raise ValueError('size must be nonnegative')
            self.n = values
            self.bit = [0] * (values + 1)
        else:
            values = list(values)
            n = len(values)
            bit = [0] + values
            for index in range(1, n + 1):
                parent = index + (index & -index)
                if parent <= n:
                    bit[parent] += bit[index]
            self.n = n
            self.bit = bit

    def add(self, index, value):
        """a[index]へvalueを加える。"""
        index += 1
        bit = self.bit
        while index <= self.n:
            bit[index] += value
            index += index & -index

    def prefix_sum(self, right):
        """半開区間[0, right)の和を返す。"""
        result = 0
        bit = self.bit
        while right:
            result += bit[right]
            right &= right - 1
        return result

    def sum(self, left, right=None):
        """[left, right)の和を返す。right省略時は[0, left)の和。"""
        if right is None:
            return self.prefix_sum(left)
        return self.prefix_sum(right) - self.prefix_sum(left)

    def get(self, index):
        """a[index]を返す。"""
        return self.sum(index, index + 1)

    def set(self, index, value):
        """a[index]をvalueへ置き換える。"""
        self.add(index, value - self.get(index))

    def lower_bound(self, target):
        """prefix和がtarget以上になる最小の右端を返す。"""
        if target <= 0:
            return 0
        index = 0
        step = 1 << self.n.bit_length() - 1 if self.n else 0
        bit = self.bit
        while step:
            next_index = index + step
            if next_index <= self.n and bit[next_index] < target:
                target -= bit[next_index]
                index = next_index
            step >>= 1
        return index if index < self.n else self.n

    def __len__(self):
        return self.n

    def tolist(self):
        """現在の要素列をlistで返す。O(N)。"""
        values = self.bit[1:]
        for index in range(self.n, 0, -1):
            parent = index + (index & -index)
            if parent <= self.n:
                values[parent - 1] -= values[index - 1]
        return values

    def __str__(self):
        return str(self.tolist())

    def __repr__(self):
        return 'BIT(%r)' % self.tolist()
import sys

def solve():
    data = iter(map(int, sys.stdin.buffer.read().split()))
    (n, q) = (next(data), next(data))
    values = [next(data) for _ in range(n)]
    graph = [[] for _ in range(n)]
    for _ in range(n - 1):
        (u, v) = (next(data), next(data))
        graph[u].append(v)
        graph[v].append(u)
    tree = HeavyLightDecomposition(graph)
    bit = BIT([values[v] for v in tree.rev])
    answer = []
    for _ in range(q):
        (kind, u, v) = (next(data), next(data), next(data))
        if kind == 0:
            bit.add(tree.tin[u], v)
        else:
            answer.append(str(sum((bit.sum(l, r) for (l, r) in tree.path(u, v)))))
    print('\n'.join(answer))
if __name__ == '__main__':
    solve()
