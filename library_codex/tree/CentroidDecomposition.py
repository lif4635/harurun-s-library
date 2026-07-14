from bisect import bisect_left


class CentroidDecomposition:
    __slots__ = (
        "n",
        "graph",
        "parent",
        "depth",
        "children",
        "root",
        "order",
        "paths",
        "built",
    )

    def __init__(self, tree, build=True):
        if isinstance(tree, int):
            if tree <= 0:
                raise ValueError("size must be positive")
            self.n = tree
            self.graph = [[] for _ in range(tree)]
            self.built = False
        else:
            self.graph = [list(row) for row in tree]
            self.n = len(self.graph)
            if self.n == 0:
                raise ValueError("tree must be nonempty")
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
            raise RuntimeError("decomposition is already built")
        if not (0 <= first < self.n and 0 <= second < self.n):
            raise IndexError("vertex is out of range")
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
                    raise ValueError("graph must be a tree")
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
        return centroid, order

    def build(self):
        if self.built:
            return self.root
        n = self.n
        graph = self.graph
        if sum(map(len, graph)) != (n - 1) << 1:
            raise ValueError("graph must be a tree")
        removed = bytearray(n)
        parent = [-1] * n
        depth = [0] * n
        children = [[] for _ in range(n)]
        paths = [[] for _ in range(n)]
        order = []
        tasks = [(0, -1, 0)]
        while tasks:
            start, centroid_parent, centroid_depth = tasks.pop()
            if removed[start]:
                continue
            centroid, component = self._component(start, removed)
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
                    node, par, distance = stack.pop()
                    paths[node].append((centroid, distance, branch))
                    for other in graph[node]:
                        if other != par and not removed[other]:
                            stack.append((other, node, distance + 1))
                tasks.append((neighbor, centroid, centroid_depth + 1))
                branch += 1
        if len(order) != n:
            raise ValueError("graph must be connected")
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
            return [], []
        vertices = [start]
        parents = [-1]
        for index, node in enumerate(vertices):
            par = parents[index]
            for other in self.graph[node]:
                if other != par and self.depth[other] >= layer:
                    vertices.append(other)
                    parents.append(node)
        return vertices, parents


class _Fenwick:
    __slots__ = ("bit",)

    def __init__(self, size):
        self.bit = [0] * (size + 1)

    def add(self, index, value):
        bit = self.bit
        index += 1
        while index < len(bit):
            bit[index] += value
            index += index & -index

    def prefix(self, right):
        bit = self.bit
        result = 0
        while right:
            result += bit[right]
            right &= right - 1
        return result

    def range_sum(self, left, right):
        return self.prefix(right) - self.prefix(left)


class CentroidDistanceFenwick:
    """Point add and distance-range sum on a static unweighted tree."""

    __slots__ = (
        "decomposition",
        "coordinates",
        "bits",
        "branch_coordinates",
        "branch_bits",
        "values",
    )

    def __init__(self, tree, values=None):
        decomposition = CentroidDecomposition(tree)
        n = decomposition.n
        coordinates = [[] for _ in range(n)]
        branch_coordinates = {}
        for vertex in range(n):
            for centroid, distance, branch in decomposition.paths[vertex]:
                coordinates[centroid].append(distance)
                if branch >= 0:
                    branch_coordinates.setdefault(
                        (centroid, branch), []
                    ).append(distance)
        coordinates = [sorted(set(row)) for row in coordinates]
        branch_coordinates = {
            key: sorted(set(row))
            for key, row in branch_coordinates.items()
        }
        self.decomposition = decomposition
        self.coordinates = coordinates
        self.bits = [_Fenwick(len(row)) for row in coordinates]
        self.branch_coordinates = branch_coordinates
        self.branch_bits = {
            key: _Fenwick(len(row))
            for key, row in branch_coordinates.items()
        }
        self.values = [0] * n
        if values is not None:
            values = list(values)
            if len(values) != n:
                raise ValueError("values has wrong length")
            for vertex, value in enumerate(values):
                if value:
                    self.add(vertex, value)

    def add(self, vertex, delta):
        self.values[vertex] += delta
        for centroid, distance, branch in self.decomposition.paths[vertex]:
            row = self.coordinates[centroid]
            self.bits[centroid].add(bisect_left(row, distance), delta)
            if branch >= 0:
                key = (centroid, branch)
                row = self.branch_coordinates[key]
                self.branch_bits[key].add(
                    bisect_left(row, distance), delta
                )

    def set(self, vertex, value):
        self.add(vertex, value - self.values[vertex])

    @staticmethod
    def _range(bit, coordinates, left, right):
        begin = bisect_left(coordinates, left)
        end = bisect_left(coordinates, right)
        return bit.range_sum(begin, end)

    def query(self, vertex, lower=0, upper=None):
        if upper is None:
            upper = self.decomposition.n + 1
        if lower >= upper:
            return 0
        answer = 0
        for centroid, distance, branch in self.decomposition.paths[vertex]:
            left = lower - distance
            right = upper - distance
            if right <= 0:
                continue
            row = self.coordinates[centroid]
            answer += self._range(
                self.bits[centroid], row, max(0, left), right
            )
            if branch >= 0:
                key = (centroid, branch)
                row = self.branch_coordinates[key]
                answer -= self._range(
                    self.branch_bits[key], row, max(0, left), right
                )
        return answer

    range_sum = query
