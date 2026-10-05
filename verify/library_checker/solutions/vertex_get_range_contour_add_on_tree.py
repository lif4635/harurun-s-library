from bisect import bisect_left

def tree_centroid(tree):
    """Return vertices whose removal leaves no component larger than half."""
    n = len(tree)
    if n == 0:
        return []
    parent = [-2] * n
    parent[0] = -1
    order = [0]
    for vertex in order:
        for other in tree[vertex]:
            if other == parent[vertex]:
                continue
            if parent[other] != -2:
                raise ValueError('graph must be a tree')
            parent[other] = vertex
            order.append(other)
    if len(order) != n:
        raise ValueError('graph must be connected')
    size = [1] * n
    for vertex in reversed(order[1:]):
        size[parent[vertex]] += size[vertex]
    result = []
    for vertex in range(n):
        largest = n - size[vertex]
        for other in tree[vertex]:
            if parent[other] == vertex and size[other] > largest:
                largest = size[other]
        if largest * 2 <= n:
            result.append(vertex)
    return result

class CentroidDecomposition:
    __slots__ = ('n', 'graph', 'parent', 'depth', 'children', 'root', 'order', 'paths', 'built')

    def __init__(self, tree, build=True):
        if isinstance(tree, int):
            if tree <= 0:
                raise ValueError('size must be positive')
            self.n = tree
            self.graph = [[] for _ in range(tree)]
            self.built = False
        else:
            self.graph = [list(row) for row in tree]
            self.n = len(self.graph)
            if self.n == 0:
                raise ValueError('tree must be nonempty')
            self.built = False
        self.parent = []
        self.depth = []
        self.children = []
        self.root = -1
        self.order = []
        self.paths = []
        if not isinstance(tree, int) and build:
            self.build()

    def add_edge(self, first, second):
        if self.built:
            raise RuntimeError('decomposition is already built')
        if not (0 <= first < self.n and 0 <= second < self.n):
            raise IndexError('vertex is out of range')
        self.graph[first].append(second)
        self.graph[second].append(first)

    def _component(self, start, removed):
        parent = {start: -1}
        order = [start]
        graph = self.graph
        for node in order:
            for other in graph[node]:
                if removed[other] or other == parent[node]:
                    continue
                if other in parent:
                    raise ValueError('graph must be a tree')
                parent[other] = node
                order.append(other)
        size = {node: 1 for node in order}
        for node in reversed(order[1:]):
            size[parent[node]] += size[node]
        total = len(order)
        centroid = start
        for node in order:
            largest = total - size[node]
            for other in graph[node]:
                if parent.get(other) == node and size[other] > largest:
                    largest = size[other]
            if largest * 2 <= total:
                centroid = node
                break
        return (centroid, order)

    def build(self):
        if self.built:
            return self.root
        n = self.n
        graph = self.graph
        if sum(map(len, graph)) != n - 1 << 1:
            raise ValueError('graph must be a tree')
        removed = bytearray(n)
        parent = [-1] * n
        depth = [0] * n
        children = [[] for _ in range(n)]
        paths = [[] for _ in range(n)]
        order = []
        tasks = [(0, -1, 0)]
        while tasks:
            (start, centroid_parent, centroid_depth) = tasks.pop()
            if removed[start]:
                continue
            (centroid, component) = self._component(start, removed)
            parent[centroid] = centroid_parent
            depth[centroid] = centroid_depth
            if centroid_parent >= 0:
                children[centroid_parent].append(centroid)
            order.append(centroid)
            removed[centroid] = 1
            paths[centroid].append((centroid, 0, -1))
            branch = 0
            for neighbor in graph[centroid]:
                if removed[neighbor]:
                    continue
                stack = [(neighbor, centroid, 1)]
                while stack:
                    (node, par, distance) = stack.pop()
                    paths[node].append((centroid, distance, branch))
                    for other in graph[node]:
                        if other != par and (not removed[other]):
                            stack.append((other, node, distance + 1))
                tasks.append((neighbor, centroid, centroid_depth + 1))
                branch += 1
        if len(order) != n:
            raise ValueError('graph must be connected')
        self.parent = parent
        self.depth = depth
        self.children = children
        self.root = order[0]
        self.order = order
        self.paths = paths
        self.built = True
        return self.root
    run = build

    def ancestors(self, vertex):
        return self.paths[vertex]

    def bfs_layer(self, start, layer):
        if self.depth[start] < layer:
            return ([], [])
        vertices = [start]
        parents = [-1]
        for (index, node) in enumerate(vertices):
            par = parents[index]
            for other in self.graph[node]:
                if other != par and self.depth[other] >= layer:
                    vertices.append(other)
                    parents.append(node)
        return (vertices, parents)

class CentroidDistanceFenwick:
    """Point add and distance-range sum on a static unweighted tree."""
    __slots__ = ('decomposition', 'bits', 'branch_bits', 'values')

    def __init__(self, tree, values=None):
        decomposition = CentroidDecomposition(tree)
        n = decomposition.n
        values = [0] * n if values is None else list(values)
        if len(values) != n:
            raise ValueError('values has wrong length')
        paths = decomposition.paths
        lengths = [2] * n
        branch_lengths = [1] * n
        for path in paths:
            child = -1
            for (centroid, distance, _) in reversed(path):
                if lengths[centroid] < distance + 2:
                    lengths[centroid] = distance + 2
                if child >= 0 and branch_lengths[child] < distance + 2:
                    branch_lengths[child] = distance + 2
                child = centroid
        bits = [[0] * length for length in lengths]
        branch_bits = [[0] * length for length in branch_lengths]
        for (vertex, path) in enumerate(paths):
            value = values[vertex]
            child = -1
            for (centroid, distance, _) in reversed(path):
                bits[centroid][distance + 1] += value
                if child >= 0:
                    branch_bits[child][distance + 1] += value
                child = centroid
        for bit in bits + branch_bits:
            for index in range(1, len(bit)):
                parent = index + (index & -index)
                if parent < len(bit):
                    bit[parent] += bit[index]
        self.decomposition = decomposition
        self.bits = bits
        self.branch_bits = branch_bits
        self.values = values

    def add(self, vertex, delta):
        self.values[vertex] += delta
        child = -1
        for (centroid, distance, _) in reversed(self.decomposition.paths[vertex]):
            bit = self.bits[centroid]
            index = distance + 1
            while index < len(bit):
                bit[index] += delta
                index += index & -index
            if child >= 0:
                bit = self.branch_bits[child]
                index = distance + 1
                while index < len(bit):
                    bit[index] += delta
                    index += index & -index
            child = centroid

    def set(self, vertex, value):
        self.add(vertex, value - self.values[vertex])

    def query(self, vertex, lower=0, upper=None):
        if upper is None:
            upper = self.decomposition.n + 1
        if not isinstance(lower, int):
            lower = bisect_left(range(self.decomposition.n + 1), lower)
        if not isinstance(upper, int):
            upper = bisect_left(range(self.decomposition.n + 1), upper)
        if lower >= upper:
            return 0
        answer = 0
        child = -1
        for (centroid, distance, _) in reversed(self.decomposition.paths[vertex]):
            left = lower - distance
            right = upper - distance
            if right > 0:
                if left < 0:
                    left = 0
                bit = self.bits[centroid]
                size = len(bit) - 1
                end = min(right, size)
                begin = min(left, size)
                while end > begin:
                    answer += bit[end]
                    end &= end - 1
                while begin > end:
                    answer -= bit[begin]
                    begin &= begin - 1
                if child >= 0:
                    bit = self.branch_bits[child]
                    size = len(bit) - 1
                    end = min(right, size)
                    begin = min(left, size)
                    while end > begin:
                        answer -= bit[end]
                        end &= end - 1
                    while begin > end:
                        answer += bit[begin]
                        begin &= begin - 1
            child = centroid
        return answer
    range_sum = query

    def tolist(self):
        return self.values[:]

    def __str__(self):
        return str(self.tolist())

    def __repr__(self):
        return 'CentroidDistanceFenwick(%r)' % self.tolist()
'重みなし木で、距離が指定範囲に入る頂点へ加算し、頂点値を取得する。'
from bisect import bisect_left as _tree_centroid_distance_add_bisect_left

class CentroidDistanceAdd:
    __slots__ = ('decomposition', 'bits', 'branch_bits', 'values')

    def __init__(self, tree, values=None):
        decomposition = CentroidDecomposition(tree)
        n = decomposition.n
        values = [0] * n if values is None else list(values)
        if len(values) != n:
            raise ValueError('values has wrong length')
        lengths = [2] * n
        branch_lengths = [1] * n
        for path in decomposition.paths:
            child = -1
            for (centroid, distance, _) in reversed(path):
                if lengths[centroid] < distance + 2:
                    lengths[centroid] = distance + 2
                if child >= 0 and branch_lengths[child] < distance + 2:
                    branch_lengths[child] = distance + 2
                child = centroid
        self.decomposition = decomposition
        self.bits = [[0] * length for length in lengths]
        self.branch_bits = [[0] * length for length in branch_lengths]
        self.values = values

    def add(self, vertex, lower, upper, delta):
        if upper is None:
            upper = self.decomposition.n + 1
        if not isinstance(lower, int):
            lower = _tree_centroid_distance_add_bisect_left(range(self.decomposition.n + 1), lower)
        if not isinstance(upper, int):
            upper = _tree_centroid_distance_add_bisect_left(range(self.decomposition.n + 1), upper)
        if lower >= upper:
            return
        child = -1
        for (centroid, distance, _) in reversed(self.decomposition.paths[vertex]):
            left = max(0, lower - distance)
            right = upper - distance
            if left < right:
                bit = self.bits[centroid]
                index = left + 1
                while index < len(bit):
                    bit[index] += delta
                    index += index & -index
                index = right + 1
                while index < len(bit):
                    bit[index] -= delta
                    index += index & -index
                if child >= 0:
                    bit = self.branch_bits[child]
                    index = left + 1
                    while index < len(bit):
                        bit[index] += delta
                        index += index & -index
                    index = right + 1
                    while index < len(bit):
                        bit[index] -= delta
                        index += index & -index
            child = centroid

    def get(self, vertex):
        result = self.values[vertex]
        child = -1
        for (centroid, distance, _) in reversed(self.decomposition.paths[vertex]):
            bit = self.bits[centroid]
            index = distance + 1
            while index:
                result += bit[index]
                index &= index - 1
            if child >= 0:
                bit = self.branch_bits[child]
                index = distance + 1
                while index:
                    result -= bit[index]
                    index &= index - 1
            child = centroid
        return result

    def tolist(self):
        return [self.get(vertex) for vertex in range(self.decomposition.n)]

    def __str__(self):
        return str(self.tolist())

    def __repr__(self):
        return 'CentroidDistanceAdd(%r)' % self.tolist()
import sys

def main():
    read = sys.stdin.buffer.readline
    (n, q) = map(int, read().split())
    values = list(map(int, read().split()))
    graph = [[] for _ in range(n)]
    for _ in range(n - 1):
        (u, v) = map(int, read().split())
        graph[u].append(v)
        graph[v].append(u)
    tree = CentroidDistanceAdd(graph, values)
    result = []
    for _ in range(q):
        query = list(map(int, read().split()))
        if query[0] == 0:
            tree.add(query[1], query[2], query[3], query[4])
        else:
            result.append(str(tree.get(query[1])))
    sys.stdout.write('\n'.join(result))
if __name__ == '__main__':
    main()
