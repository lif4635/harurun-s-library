class StaticRMQ:
    __slots__ = ('n', 'block_size', 'block_shift', 'block_mask', 'values', 'masks', 'prefix_min', 'suffix_min', 'table')

    def __init__(self, values):
        values = list(values)
        n = len(values)
        logn = max(1, n.bit_length())
        block_size = 1 << (logn - 1).bit_length()
        block_shift = block_size.bit_length() - 1
        masks = [0] * n
        prefix_min = [0] * n
        suffix_min = [0] * n
        block_min = []
        for left in range(0, n, block_size):
            right = min(left + block_size, n)
            mask = 0
            best = left
            for i in range(left, right):
                x = values[i]
                while mask:
                    top = mask.bit_length() - 1
                    if values[left + top] <= x:
                        break
                    mask ^= 1 << top
                mask |= 1 << i - left
                masks[i] = mask
                if values[i] < values[best]:
                    best = i
                prefix_min[i] = best
            block_min.append(best)
            best = right - 1
            for i in range(right - 1, left - 1, -1):
                if values[i] <= values[best]:
                    best = i
                suffix_min[i] = best
        table = []
        if block_min:
            table.append(block_min)
            width = 2
            while width <= len(block_min):
                half = width >> 1
                prev = table[-1]
                cur = [0] * (len(block_min) - width + 1)
                for i in range(len(cur)):
                    x = prev[i]
                    y = prev[i + half]
                    cur[i] = x if values[x] <= values[y] else y
                table.append(cur)
                width <<= 1
        self.n = n
        self.block_size = block_size
        self.block_shift = block_shift
        self.block_mask = block_size - 1
        self.values = values
        self.masks = masks
        self.prefix_min = prefix_min
        self.suffix_min = suffix_min
        self.table = table

    def _small_argmin(self, l, r):
        base = l >> self.block_shift << self.block_shift
        mask = self.masks[r - 1] & ~((1 << (l & self.block_mask)) - 1)
        return base + ((mask & -mask).bit_length() - 1)

    def argmin(self, l, r):
        assert 0 <= l < r <= self.n
        shift = self.block_shift
        left_block = l >> shift
        right_block = r - 1 >> shift
        if left_block == right_block:
            return self._small_argmin(l, r)
        best = self.suffix_min[l]
        first = left_block + 1
        last = right_block
        if first < last:
            level = (last - first).bit_length() - 1
            width = 1 << level
            table = self.table[level]
            x = table[first]
            y = table[last - width]
            middle = x if self.values[x] <= self.values[y] else y
            if self.values[middle] < self.values[best]:
                best = middle
        right = self.prefix_min[r - 1]
        if self.values[right] < self.values[best]:
            best = right
        return best

    def query(self, l, r):
        return self.values[self.argmin(l, r)]
    prod = query

    def __len__(self):
        return self.n
'木のEuler tour順と部分木区間を構築する。'

def _tree_euler_tour_edge(entry):
    if isinstance(entry, int):
        return (entry, 1)
    return (entry[0], entry[1])

class EulerTour:
    __slots__ = ('n', 'down', 'up', 'parent', 'depth', 'component', 'tour', 'tour_depth', 'rmq')

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
            raise IndexError('root is out of range')
        down = [-1] * n
        up = [-1] * n
        parent = [-2] * n
        depth = [0] * n
        component = [-1] * n
        tour = []
        tour_depth = []
        starts = [root]
        starts.extend((node for node in range(n) if node != root))
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
                (node, par, index) = stack[-1]
                if index == len(tree[node]):
                    up[node] = len(tour)
                    stack.pop()
                    if par >= 0:
                        tour.append(par)
                        tour_depth.append(depth[par])
                    continue
                entry = tree[node][index]
                stack[-1][2] = index + 1
                (other, _) = _tree_euler_tour_edge(entry)
                if other == par:
                    continue
                if not 0 <= other < n or parent[other] != -2:
                    raise ValueError('graph must be a forest')
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
        self.rmq = StaticRMQ([(tour_depth[index], tour[index]) for index in range(len(tour))])

    def idx(self, node):
        return (self.down[node], self.up[node])

    def lca(self, first, second):
        if self.component[first] != self.component[second]:
            return -1
        left = self.down[first]
        right = self.down[second]
        if left > right:
            (left, right) = (right, left)
        return self.rmq.query(left, right + 1)[1]

    def distance(self, first, second):
        ancestor = self.lca(first, second)
        if ancestor < 0:
            return -1
        return self.depth[first] + self.depth[second] - (self.depth[ancestor] << 1)
    dist = distance

    def node_intervals(self, first, second):
        ancestor = self.lca(first, second)
        if ancestor < 0:
            return []
        return [(self.down[ancestor], self.down[first] + 1), (self.down[ancestor] + 1, self.down[second] + 1)]
    node_query = node_intervals

    def edge_intervals(self, first, second):
        ancestor = self.lca(first, second)
        if ancestor < 0:
            return []
        left = self.down[ancestor] + 1
        return [(left, self.down[first] + 1), (left, self.down[second] + 1)]
    edge_query = edge_intervals

    def subtree_interval(self, node):
        return (self.down[node], self.up[node])
    subtree_query = subtree_interval

    def __len__(self):
        return len(self.tour)
'木または森の2頂点に対するLCAと距離を取得する。'

class LCA:
    """Euler tourとRMQでLCAをO(1)で返す。"""
    __slots__ = ('n', 'parent', 'depth', 'component', '_euler')

    def __init__(self, tree, root=0):
        """Euler tourとRMQを構築する。O(N)。"""
        euler = EulerTour(tree, root)
        self.n = euler.n
        self.parent = euler.parent
        self.depth = euler.depth
        self.component = euler.component
        self._euler = euler

    def __call__(self, first, second):
        """firstとsecondのLCAを返す。異なる連結成分なら-1。O(1)。"""
        return self._euler.lca(first, second)

    def dist(self, first, second):
        """firstとsecondの辺数距離を返す。異なる連結成分なら-1。O(1)。"""
        return self._euler.distance(first, second)

    def on_path(self, vertex, first, second):
        """Return whether ``vertex`` lies on the closed first--second path."""
        distance = self.dist(first, second)
        return distance >= 0 and self.dist(first, vertex) + self.dist(vertex, second) == distance

    def path_intersection(self, first, second, third, fourth):
        """Return endpoints of two closed paths' intersection, or ``None``."""
        if self.component[first] != self.component[second] or self.component[third] != self.component[fourth] or self.component[first] != self.component[third]:
            return None
        vertices = [first, second, third, fourth]
        candidates = set(vertices)
        for i in range(4):
            for j in range(i):
                candidates.add(self(vertices[i], vertices[j]))
        common = [vertex for vertex in candidates if self.on_path(vertex, first, second) and self.on_path(vertex, third, fourth)]
        if not common:
            return None
        endpoint_first = common[0]
        endpoint_second = common[0]
        best = 0
        for (i, vertex) in enumerate(common):
            for other in common[:i]:
                distance = self.dist(vertex, other)
                if distance > best:
                    best = distance
                    endpoint_first = vertex
                    endpoint_second = other
        return (endpoint_first, endpoint_second)
import sys

def solve():
    read = sys.stdin.buffer.readline
    (n, q) = map(int, read().split())
    parents = list(map(int, read().split()))
    tree = [[] for _ in range(n)]
    for (v, p) in enumerate(parents, 1):
        tree[v].append(p)
        tree[p].append(v)
    solver = LCA(tree)
    answer = []
    for _ in range(q):
        (u, v) = map(int, read().split())
        answer.append(solver(u, v))
    print('\n'.join(map(str, answer)))
solve()
