VERTEX = 0
EDGE = 0
COMPRESS = 1
RAKE = 2
ADD_EDGE = 3
ADD_VERTEX = 4


def _root_tree(graph, root):
    n = len(graph)
    if n == 0:
        raise ValueError("tree must be nonempty")
    if not 0 <= root < n:
        raise IndexError("root is out of range")
    parent = [-2] * n
    parent[root] = -1
    order = [root]
    for node in order:
        for other in graph[node]:
            if other == parent[node]:
                continue
            if not 0 <= other < n:
                raise IndexError("vertex is out of range")
            if parent[other] != -2:
                raise ValueError("graph is not a tree")
            parent[other] = node
            order.append(other)
    if len(order) != n:
        raise ValueError("graph is not connected")
    size = [1] * n
    for node in reversed(order[1:]):
        size[parent[node]] += size[node]
    children = [[] for _ in range(n)]
    heavy = [-1] * n
    for node in order:
        best_size = 0
        for other in graph[node]:
            if parent[other] == node:
                children[node].append(other)
                if size[other] > best_size:
                    best_size = size[other]
                    heavy[node] = other
        best = heavy[node]
        if best >= 0 and children[node][0] != best:
            index = children[node].index(best)
            children[node][0], children[node][index] = (
                children[node][index],
                children[node][0],
            )
    return parent, order, size, children, heavy


class StaticTopTree:
    """Balanced edge-cluster static top tree.

    Original node ``v`` is the leaf for the edge ``parent[v] -> v``.  The
    root leaf is a dummy edge, which is useful as an identity cluster.
    """

    __slots__ = (
        "n",
        "graph",
        "root",
        "top_tree_root",
        "parent",
        "left",
        "right",
        "type",
        "tree_parent",
        "subtree_size",
        "children",
        "heavy",
        "built",
    )

    def __init__(self, tree, root=0):
        if isinstance(tree, int):
            if tree <= 0:
                raise ValueError("size must be positive")
            self.n = tree
            self.graph = [[] for _ in range(tree)]
            self.root = root
            self.parent = []
            self.left = []
            self.right = []
            self.type = []
            self.tree_parent = []
            self.subtree_size = []
            self.children = []
            self.heavy = []
            self.top_tree_root = -1
            self.built = False
        else:
            graph = [list(row) for row in tree]
            self.n = len(graph)
            self.graph = graph
            self.root = root
            self.parent = []
            self.left = []
            self.right = []
            self.type = []
            self.tree_parent = []
            self.subtree_size = []
            self.children = []
            self.heavy = []
            self.top_tree_root = -1
            self.built = False
            self.build(root)

    @classmethod
    def from_edges(cls, size, edges, root=0):
        result = cls(size, root)
        for first, second in edges:
            result.add_edge(first, second)
        result.build(root)
        return result

    def add_edge(self, first, second):
        if self.built:
            raise RuntimeError("top tree is already built")
        if not (0 <= first < self.n and 0 <= second < self.n):
            raise IndexError("vertex is out of range")
        self.graph[first].append(second)
        self.graph[second].append(first)

    def _add_cluster(self, left, right, cluster_type):
        node = len(self.parent)
        self.parent.append(-1)
        self.left.append(left)
        self.right.append(right)
        self.type.append(cluster_type)
        self.parent[left] = node
        self.parent[right] = node
        return node

    def _merge(self, items, cluster_type):
        if len(items) == 1:
            return items[0]
        prefix = [0]
        for _, size in items:
            prefix.append(prefix[-1] + size)
        result = []
        tasks = [(0, len(items), 0, 0)]
        while tasks:
            left, right, state, middle = tasks.pop()
            if right - left == 1:
                result.append(items[left])
                continue
            if state == 0:
                total = prefix[right] - prefix[left]
                low = left
                high = right - 1
                while low < high:
                    mid = (low + high) >> 1
                    before = prefix[mid] - prefix[left]
                    weight = prefix[mid + 1] - prefix[mid]
                    if total > (before << 1) + weight:
                        low = mid + 1
                    else:
                        high = mid
                middle = low
                tasks.append((left, right, 1, middle))
                tasks.append((middle, right, 0, 0))
                tasks.append((left, middle, 0, 0))
            else:
                second = result.pop()
                first = result.pop()
                node = self._add_cluster(
                    first[0], second[0], cluster_type
                )
                result.append((node, first[1] + second[1]))
        return result[0]

    def build(self, root=None):
        if self.built:
            return self.top_tree_root
        if root is not None:
            self.root = root
        (
            tree_parent,
            order,
            size,
            children,
            heavy,
        ) = _root_tree(self.graph, self.root)
        n = self.n
        self.parent = [-1] * n
        self.left = [-1] * n
        self.right = [-1] * n
        self.type = [EDGE] * n
        self.tree_parent = tree_parent
        self.subtree_size = size
        self.children = children
        self.heavy = heavy
        starts = [
            node
            for node in order
            if tree_parent[node] < 0
            or heavy[tree_parent[node]] != node
        ]
        chain_root = [-1] * n
        for start in reversed(starts):
            path = []
            node = start
            while node >= 0:
                path.append(node)
                node = heavy[node]
            clusters = [(path[0], 1)]
            for index in range(1, len(path)):
                previous = path[index - 1]
                node = path[index]
                rake_items = [(node, 1)]
                for child in children[previous][1:]:
                    rake_items.append(
                        (chain_root[child], size[child])
                    )
                clusters.append(self._merge(rake_items, RAKE))
            root_cluster, total = self._merge(clusters, COMPRESS)
            if total != size[start]:
                raise AssertionError("invalid top tree cluster size")
            chain_root[start] = root_cluster
        self.top_tree_root = chain_root[self.root]
        self.built = True
        return self.top_tree_root

    run = build

    def height(self):
        depth = [(self.top_tree_root, 1)]
        answer = 0
        while depth:
            node, value = depth.pop()
            if value > answer:
                answer = value
            left = self.left[node]
            if left >= 0:
                depth.append((left, value + 1))
                depth.append((self.right[node], value + 1))
        return answer


class StaticTopTreeEdgeBased(StaticTopTree):
    __slots__ = ()


class DynamicTreeDP:
    __slots__ = ("top_tree", "data", "compress", "rake")

    def __init__(self, top_tree, vertex, rake, compress):
        if not top_tree.built:
            top_tree.build()
        self.top_tree = top_tree
        self.compress = compress
        self.rake = rake
        n = top_tree.n
        data = [None] * len(top_tree.parent)
        for node in range(n):
            data[node] = vertex(node)
        self.data = data
        for node in range(n, len(data)):
            self._update(node)

    def _update(self, node):
        tree = self.top_tree
        left = self.data[tree.left[node]]
        right = self.data[tree.right[node]]
        if tree.type[node] == COMPRESS:
            self.data[node] = self.compress(left, right)
        else:
            self.data[node] = self.rake(left, right)

    def set(self, node, value):
        self.data[node] = value
        node = self.top_tree.parent[node]
        while node >= 0:
            self._update(node)
            node = self.top_tree.parent[node]

    def update(self, node):
        node = self.top_tree.parent[node]
        while node >= 0:
            self._update(node)
            node = self.top_tree.parent[node]

    def get(self):
        return self.data[self.top_tree.top_tree_root]


class EdgeTopTreeDP:
    __slots__ = ("top_tree", "data", "edge", "compress", "rake")

    def __init__(self, top_tree, edge, compress, rake):
        if not top_tree.built:
            top_tree.build()
        self.top_tree = top_tree
        self.edge = edge
        self.compress = compress
        self.rake = rake
        data = [None] * len(top_tree.parent)
        self.data = data
        order = []
        stack = [top_tree.top_tree_root]
        while stack:
            node = stack.pop()
            order.append(node)
            left = top_tree.left[node]
            if left >= 0:
                stack.append(left)
                stack.append(top_tree.right[node])
        for node in reversed(order):
            self._update(node)

    def _update(self, node):
        tree = self.top_tree
        cluster_type = tree.type[node]
        if cluster_type == EDGE:
            self.data[node] = self.edge(node)
        elif cluster_type == COMPRESS:
            self.data[node] = self.compress(
                self.data[tree.left[node]], self.data[tree.right[node]]
            )
        else:
            self.data[node] = self.rake(
                self.data[tree.left[node]], self.data[tree.right[node]]
            )

    def update(self, edge_leaf):
        node = edge_leaf
        while node >= 0:
            self._update(node)
            node = self.top_tree.parent[node]

    def get(self):
        return self.data[self.top_tree.top_tree_root]


DPonStaticTopTree = EdgeTopTreeDP


class DynamicRerootingDP:
    __slots__ = (
        "top_tree",
        "data",
        "rake_forward",
        "rake_backward",
        "compress",
        "identity",
    )

    def __init__(
        self,
        top_tree,
        vertex,
        rake_forward,
        rake_backward,
        compress,
        identity,
    ):
        if not top_tree.built:
            top_tree.build()
        self.top_tree = top_tree
        self.rake_forward = rake_forward
        self.rake_backward = rake_backward
        self.compress = compress
        self.identity = identity
        n = top_tree.n
        data = [None] * len(top_tree.parent)
        empty = identity()
        for node in range(n):
            data[node] = (empty, empty) if node == top_tree.root else vertex(node)
        self.data = data
        for node in range(n, len(data)):
            self._update(node)

    def _update(self, node):
        tree = self.top_tree
        left = self.data[tree.left[node]]
        right = self.data[tree.right[node]]
        if tree.type[node] == COMPRESS:
            self.data[node] = (
                self.compress(left[0], right[0]),
                self.compress(right[1], left[1]),
            )
        else:
            self.data[node] = (
                self.rake_forward(left[0], right[0]),
                self.rake_backward(left[1], right[0]),
            )

    def set(self, node, value):
        self.data[node] = value
        node = self.top_tree.parent[node]
        while node >= 0:
            self._update(node)
            node = self.top_tree.parent[node]

    def get(self, vertex):
        tree = self.top_tree
        current = vertex
        first = self.data[current][1]
        second = self.identity()
        third = self.identity()
        while True:
            parent = tree.parent[current]
            if parent < 0:
                break
            left = tree.left[parent]
            right = tree.right[parent]
            if tree.type[parent] == COMPRESS:
                if left == current:
                    second = self.compress(second, self.data[right][0])
                else:
                    first = self.compress(first, self.data[left][1])
            elif left == current:
                first = self.rake_backward(first, self.data[right][0])
            else:
                third = self.compress(
                    third, self.rake_forward(first, second)
                )
                first = self.identity()
                second = self.data[left][0]
            current = parent
        return self.compress(
            third, self.rake_forward(first, second)
        )


class StaticTopTreeVertexBased:
    __slots__ = (
        "n",
        "graph",
        "root",
        "top_tree_root",
        "parent",
        "left",
        "right",
        "type",
        "tree_parent",
        "subtree_size",
        "children",
        "heavy",
    )

    def __init__(self, tree, root=0):
        graph = [list(row) for row in tree]
        self.n = len(graph)
        self.graph = graph
        self.root = root
        (
            tree_parent,
            order,
            size,
            children,
            heavy,
        ) = _root_tree(graph, root)
        n = self.n
        self.parent = [-1] * n
        self.left = [-1] * n
        self.right = [-1] * n
        self.type = [VERTEX] * n
        self.tree_parent = tree_parent
        self.subtree_size = size
        self.children = children
        self.heavy = heavy
        starts = [
            node
            for node in order
            if tree_parent[node] < 0
            or heavy[tree_parent[node]] != node
        ]
        chain_root = [-1] * n
        for start in reversed(starts):
            path_items = []
            node = start
            while node >= 0:
                light_items = []
                for child in children[node][1:]:
                    edge_cluster = self._add_unary(
                        chain_root[child], ADD_EDGE
                    )
                    light_items.append((edge_cluster, size[child]))
                if light_items:
                    rake_root, rake_size = self._merge(light_items, RAKE)
                    self.left[node] = rake_root
                    self.type[node] = ADD_VERTEX
                    self.parent[rake_root] = node
                    path_items.append((node, rake_size + 1))
                else:
                    path_items.append((node, 1))
                node = heavy[node]
            root_cluster, total = self._merge(path_items, COMPRESS)
            if total != size[start]:
                raise AssertionError("invalid top tree cluster size")
            chain_root[start] = root_cluster
        self.top_tree_root = chain_root[root]

    def _add_unary(self, child, cluster_type):
        node = len(self.parent)
        self.parent.append(-1)
        self.left.append(child)
        self.right.append(-1)
        self.type.append(cluster_type)
        self.parent[child] = node
        return node

    def _add_binary(self, left, right, cluster_type):
        node = len(self.parent)
        self.parent.append(-1)
        self.left.append(left)
        self.right.append(right)
        self.type.append(cluster_type)
        self.parent[left] = node
        self.parent[right] = node
        return node

    def _merge(self, items, cluster_type):
        if len(items) == 1:
            return items[0]
        prefix = [0]
        for _, size in items:
            prefix.append(prefix[-1] + size)
        result = []
        tasks = [(0, len(items), 0, 0)]
        while tasks:
            left, right, state, middle = tasks.pop()
            if right - left == 1:
                result.append(items[left])
                continue
            if state == 0:
                total = prefix[right] - prefix[left]
                low = left
                high = right - 1
                while low < high:
                    mid = (low + high) >> 1
                    before = prefix[mid] - prefix[left]
                    weight = prefix[mid + 1] - prefix[mid]
                    if total > (before << 1) + weight:
                        low = mid + 1
                    else:
                        high = mid
                middle = low
                tasks.append((left, right, 1, middle))
                tasks.append((middle, right, 0, 0))
                tasks.append((left, middle, 0, 0))
            else:
                second = result.pop()
                first = result.pop()
                node = self._add_binary(
                    first[0], second[0], cluster_type
                )
                result.append((node, first[1] + second[1]))
        return result[0]

    def height(self):
        stack = [(self.top_tree_root, 1)]
        answer = 0
        while stack:
            node, depth = stack.pop()
            if depth > answer:
                answer = depth
            left = self.left[node]
            right = self.right[node]
            if left >= 0:
                stack.append((left, depth + 1))
            if right >= 0:
                stack.append((right, depth + 1))
        return answer


class VertexTopTreeDP:
    __slots__ = (
        "top_tree",
        "path",
        "point",
        "vertex",
        "compress",
        "rake",
        "add_edge",
        "add_vertex",
    )

    def __init__(
        self,
        top_tree,
        vertex,
        compress,
        rake,
        add_edge,
        add_vertex,
    ):
        self.top_tree = top_tree
        self.vertex = vertex
        self.compress = compress
        self.rake = rake
        self.add_edge = add_edge
        self.add_vertex = add_vertex
        size = len(top_tree.parent)
        self.path = [None] * size
        self.point = [None] * size
        order = []
        stack = [top_tree.top_tree_root]
        while stack:
            node = stack.pop()
            order.append(node)
            left = top_tree.left[node]
            right = top_tree.right[node]
            if left >= 0:
                stack.append(left)
            if right >= 0:
                stack.append(right)
        for node in reversed(order):
            self._update(node)

    def _update(self, node):
        tree = self.top_tree
        cluster_type = tree.type[node]
        if cluster_type == VERTEX:
            self.path[node] = self.vertex(node)
        elif cluster_type == COMPRESS:
            self.path[node] = self.compress(
                self.path[tree.left[node]], self.path[tree.right[node]]
            )
        elif cluster_type == RAKE:
            self.point[node] = self.rake(
                self.point[tree.left[node]], self.point[tree.right[node]]
            )
        elif cluster_type == ADD_EDGE:
            self.point[node] = self.add_edge(self.path[tree.left[node]])
        else:
            self.path[node] = self.add_vertex(
                self.point[tree.left[node]], node
            )

    def update(self, vertex):
        node = vertex
        while node >= 0:
            self._update(node)
            node = self.top_tree.parent[node]

    def get(self):
        return self.path[self.top_tree.top_tree_root]


DPonStaticTopTreeVertexBased = VertexTopTreeDP
