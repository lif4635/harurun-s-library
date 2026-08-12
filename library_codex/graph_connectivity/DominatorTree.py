"""有向グラフで始点から各頂点への全経路が必ず通る直前の支配頂点を求める。"""


def dominator_tree(graph, root=0):
    """各頂点のimmediate dominatorを頂点順のlistで返す。"""
    size = len(graph)
    if not 0 <= root < size:
        raise ValueError("root must be a vertex of graph")

    adjacency = [[] for _ in range(size)]
    reverse = [[] for _ in range(size)]
    for source, row in enumerate(graph):
        output = adjacency[source]
        for entry in row:
            target = entry if isinstance(entry, int) else entry[0]
            if not 0 <= target < size:
                raise ValueError("edge endpoint is outside graph")
            output.append(target)
            reverse[target].append(source)

    order_index = [-1] * size
    parent = [-1] * size
    order = [root]
    order_index[root] = 0
    stack = [(root, 0)]
    while stack:
        vertex, edge_index = stack[-1]
        if edge_index == len(adjacency[vertex]):
            stack.pop()
            continue
        target = adjacency[vertex][edge_index]
        stack[-1] = (vertex, edge_index + 1)
        if order_index[target] < 0:
            parent[target] = vertex
            order_index[target] = len(order)
            order.append(target)
            stack.append((target, 0))

    semi = list(range(size))
    label = list(range(size))
    ancestor = [-1] * size
    representative = list(range(size))
    buckets = [[] for _ in range(size)]

    def compress(vertex):
        path = []
        current = vertex
        while ancestor[current] >= 0:
            path.append(current)
            current = ancestor[current]
        while path:
            node = path.pop()
            upper = ancestor[node]
            if order_index[semi[label[upper]]] < order_index[semi[label[node]]]:
                label[node] = label[upper]
            ancestor[node] = current

    for position in range(len(order) - 1, 0, -1):
        vertex = order[position]
        for source in reverse[vertex]:
            if order_index[source] < 0:
                continue
            compress(source)
            candidate = semi[label[source]]
            if order_index[candidate] < order_index[semi[vertex]]:
                semi[vertex] = candidate
        buckets[semi[vertex]].append(vertex)

        tree_parent = parent[vertex]
        for pending in buckets[tree_parent]:
            compress(pending)
            representative[pending] = label[pending]
        buckets[tree_parent].clear()
        ancestor[vertex] = tree_parent

    immediate = [-1] * size
    immediate[root] = root
    for vertex in order[1:]:
        candidate = representative[vertex]
        if semi[vertex] == semi[candidate]:
            immediate[vertex] = semi[vertex]
        else:
            immediate[vertex] = immediate[candidate]
    return immediate


class DominatorTree:
    """Immediate dominator treeを構築し、支配関係を繰り返しqueryする。"""

    __slots__ = (
        "n", "root", "idom", "tree", "depth", "up", "tin", "tout",
    )

    def __init__(self, graph, root=0):
        size = len(graph)
        immediate = dominator_tree(graph, root)
        tree = [[] for _ in range(size)]
        for vertex, parent in enumerate(immediate):
            if vertex != root and parent != -1:
                tree[parent].append(vertex)

        depth = [-1] * size
        tin = [-1] * size
        tout = [-1] * size
        parent = list(range(size))
        depth[root] = 0
        timer = 0
        stack = [(root, 0)]
        while stack:
            vertex, phase = stack.pop()
            if phase == 0:
                tin[vertex] = timer
                timer += 1
                stack.append((vertex, 1))
                for child in reversed(tree[vertex]):
                    parent[child] = vertex
                    depth[child] = depth[vertex] + 1
                    stack.append((child, 0))
            else:
                tout[vertex] = timer

        levels = max(1, size.bit_length())
        up = [parent]
        for _ in range(1, levels):
            previous = up[-1]
            up.append([previous[previous[vertex]] for vertex in range(size)])

        self.n = size
        self.root = root
        self.idom = immediate
        self.tree = tree
        self.depth = depth
        self.up = up
        self.tin = tin
        self.tout = tout

    def dominates(self, dominator, vertex):
        """rootからvertexへの全pathがdominatorを通るか判定する。"""
        if not 0 <= dominator < self.n or not 0 <= vertex < self.n:
            raise IndexError("vertex is outside the graph")
        if self.depth[dominator] == -1 or self.depth[vertex] == -1:
            return False
        return (
            self.tin[dominator] <= self.tin[vertex]
            < self.tout[dominator]
        )

    def nearest_common_dominator(self, first, second):
        """二頂点をともに支配するrootから最も遠い頂点を返す。"""
        if not 0 <= first < self.n or not 0 <= second < self.n:
            raise IndexError("vertex is outside the graph")
        if self.depth[first] == -1 or self.depth[second] == -1:
            return -1
        if self.depth[first] < self.depth[second]:
            first, second = second, first
        difference = self.depth[first] - self.depth[second]
        level = 0
        while difference:
            if difference & 1:
                first = self.up[level][first]
            difference >>= 1
            level += 1
        if first == second:
            return first
        for level in range(len(self.up) - 1, -1, -1):
            if self.up[level][first] != self.up[level][second]:
                first = self.up[level][first]
                second = self.up[level][second]
        return self.up[0][first]

    def dominator_path(self, vertex):
        """rootからvertexまでの支配頂点を順に返す。"""
        if not 0 <= vertex < self.n:
            raise IndexError("vertex is outside the graph")
        if self.depth[vertex] == -1:
            return []
        path = []
        while True:
            path.append(vertex)
            if vertex == self.root:
                break
            vertex = self.idom[vertex]
        path.reverse()
        return path
