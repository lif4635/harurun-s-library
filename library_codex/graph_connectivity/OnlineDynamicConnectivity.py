from collections import namedtuple


EDGE_MARK = 1
EXACT_LEVEL = 2
ForestCutQuery = namedtuple("ForestCutQuery", "forest_cut forest_link")


class _EulerTourTree:
    __slots__ = (
        "n",
        "vertex_node",
        "edge_node",
        "left",
        "right",
        "parent",
        "flags",
        "weight",
        "aggregate_flags",
        "aggregate_size",
        "key_u",
        "key_v",
        "free",
    )

    def __init__(self, size):
        self.n = size
        self.vertex_node = [-1] * size
        self.edge_node = {}
        self.left = []
        self.right = []
        self.parent = []
        self.flags = []
        self.weight = []
        self.aggregate_flags = []
        self.aggregate_size = []
        self.key_u = []
        self.key_v = []
        self.free = []

    def _new_node(self, flags, weight, first, second):
        if self.free:
            node = self.free.pop()
            self.left[node] = -1
            self.right[node] = -1
            self.parent[node] = -1
            self.flags[node] = flags
            self.weight[node] = weight
            self.aggregate_flags[node] = flags
            self.aggregate_size[node] = weight
            self.key_u[node] = first
            self.key_v[node] = second
            return node
        node = len(self.left)
        self.left.append(-1)
        self.right.append(-1)
        self.parent.append(-1)
        self.flags.append(flags)
        self.weight.append(weight)
        self.aggregate_flags.append(flags)
        self.aggregate_size.append(weight)
        self.key_u.append(first)
        self.key_v.append(second)
        return node

    def _update(self, node):
        left = self.left[node]
        right = self.right[node]
        flags = self.flags[node]
        size = self.weight[node]
        if left >= 0:
            flags |= self.aggregate_flags[left]
            size += self.aggregate_size[left]
        if right >= 0:
            flags |= self.aggregate_flags[right]
            size += self.aggregate_size[right]
        self.aggregate_flags[node] = flags
        self.aggregate_size[node] = size

    def _rotate(self, node):
        parent = self.parent[node]
        grandparent = self.parent[parent]
        if self.left[parent] == node:
            middle = self.right[node]
            self.right[node] = parent
            self.left[parent] = middle
        else:
            middle = self.left[node]
            self.left[node] = parent
            self.right[parent] = middle
        if middle >= 0:
            self.parent[middle] = parent
        self.parent[parent] = node
        self.parent[node] = grandparent
        if grandparent >= 0:
            if self.left[grandparent] == parent:
                self.left[grandparent] = node
            else:
                self.right[grandparent] = node
        self._update(parent)
        self._update(node)

    def _splay(self, node):
        while self.parent[node] >= 0:
            parent = self.parent[node]
            grandparent = self.parent[parent]
            if grandparent < 0:
                self._rotate(node)
            elif (self.left[grandparent] == parent) == (
                self.left[parent] == node
            ):
                self._rotate(parent)
                self._rotate(node)
            else:
                self._rotate(node)
                self._rotate(node)
        self._update(node)
        return node

    def _front(self, root):
        root = self._splay(root)
        while self.left[root] >= 0:
            root = self.left[root]
        return self._splay(root)

    def _merge(self, first, second):
        if first < 0:
            return second
        if second < 0:
            return first
        first = self._splay(first)
        second = self._front(second)
        self.left[second] = first
        self.parent[first] = second
        self._update(second)
        return second

    def _split_left(self, node):
        node = self._splay(node)
        left = self.left[node]
        if left >= 0:
            self.parent[left] = -1
        self.left[node] = -1
        self._update(node)
        return left, node

    def _split_right(self, node):
        node = self._splay(node)
        right = self.right[node]
        if right >= 0:
            self.parent[right] = -1
        self.right[node] = -1
        self._update(node)
        return node, right

    def expose(self, vertex):
        node = self.vertex_node[vertex]
        if node < 0:
            node = self._new_node(0, 1, vertex, vertex)
            self.vertex_node[vertex] = node
        return self._splay(node)

    def evert(self, vertex):
        node = self.expose(vertex)
        left, right = self._split_left(node)
        return self._merge(right, left)

    def link(self, first, second, flags):
        second_root = self.evert(second)
        first_root = self.evert(first)
        forward = self._new_node(flags, 0, first, second)
        backward = self._new_node(flags, 0, second, first)
        self.edge_node[(first, second)] = forward
        self.edge_node[(second, first)] = backward
        return self._merge(
            self._merge(first_root, forward),
            self._merge(second_root, backward),
        )

    def cut(self, first, second):
        self.evert(first)
        forward = self.edge_node[(first, second)]
        backward = self.edge_node[(second, first)]
        first_root, _ = self._split_left(forward)
        self._split_right(forward)
        second_root, _ = self._split_left(backward)
        _, first_tail = self._split_right(backward)
        del self.edge_node[(first, second)]
        del self.edge_node[(second, first)]
        self.free.append(forward)
        self.free.append(backward)
        return self._merge(first_root, first_tail), second_root

    def connected(self, first, second):
        if first == second:
            return True
        first_node = self.vertex_node[first]
        second_node = self.vertex_node[second]
        if first_node < 0 or second_node < 0:
            return False
        first_node = self._splay(first_node)
        self._splay(second_node)
        return self.parent[first_node] >= 0

    def has_edge(self, first, second):
        return (first, second) in self.edge_node

    def set_vertex_flags(self, vertex, flags):
        node = self.expose(vertex)
        self.flags[node] = flags
        self._update(node)

    def set_edge_flags(self, first, second, flags):
        node = self.edge_node[(first, second)]
        self._splay(node)
        self.flags[node] = flags
        self._update(node)

    def component_data(self, vertex):
        node = self.expose(vertex)
        return self.aggregate_flags[node], self.aggregate_size[node], node

    def search_flag(self, node, mask):
        node = self._splay(node)
        if self.aggregate_flags[node] & mask == 0:
            return -1
        while True:
            if self.flags[node] & mask:
                return self._splay(node)
            left = self.left[node]
            if left >= 0 and self.aggregate_flags[left] & mask:
                node = left
            else:
                node = self.right[node]


class OnlineDynamicConnectivity:
    __slots__ = (
        "n",
        "level_count",
        "forests",
        "non_tree",
        "edge_count",
        "component_count",
    )

    def __init__(self, vertex_count):
        if vertex_count < 0:
            raise ValueError("vertex_count must be nonnegative")
        self.n = vertex_count
        self.level_count = max(1, vertex_count.bit_length() + 1)
        self.forests = [
            _EulerTourTree(vertex_count) for _ in range(self.level_count)
        ]
        self.non_tree = [{} for _ in range(self.level_count)]
        self.edge_count = {}
        self.component_count = vertex_count

    def _check_vertex(self, vertex):
        if not 0 <= vertex < self.n:
            raise ValueError("vertex index out of range")

    @staticmethod
    def _edge(first, second):
        return (first, second) if first <= second else (second, first)

    def _add_non_tree(self, level, first, second):
        adjacency = self.non_tree[level]
        first_edges = adjacency.get(first)
        if first_edges is None:
            first_edges = set()
            adjacency[first] = first_edges
            self.forests[level].set_vertex_flags(first, EDGE_MARK)
        first_edges.add(second)
        second_edges = adjacency.get(second)
        if second_edges is None:
            second_edges = set()
            adjacency[second] = second_edges
            self.forests[level].set_vertex_flags(second, EDGE_MARK)
        second_edges.add(first)

    def _erase_non_tree(self, level, first, second):
        adjacency = self.non_tree[level]
        first_edges = adjacency[first]
        first_edges.remove(second)
        if not first_edges:
            del adjacency[first]
            self.forests[level].set_vertex_flags(first, 0)
        second_edges = adjacency[second]
        second_edges.remove(first)
        if not second_edges:
            del adjacency[second]
            self.forests[level].set_vertex_flags(second, 0)

    def _replace(self, first, second):
        frames = []
        level = 0
        while level < self.level_count:
            forest = self.forests[level]
            if not forest.connected(first, second):
                break
            first_root, second_root = forest.cut(first, second)
            frames.append((level, first_root, second_root))
            level += 1
        replacement = None
        for level, first_root, second_root in reversed(frames):
            forest = self.forests[level]
            if replacement is not None:
                forest.link(replacement[0], replacement[1], 0)
                continue
            if forest.aggregate_size[first_root] > forest.aggregate_size[second_root]:
                first_root, second_root = second_root, first_root
            while forest.aggregate_flags[first_root] & EXACT_LEVEL:
                node = forest.search_flag(first_root, EXACT_LEVEL)
                edge_first = forest.key_u[node]
                edge_second = forest.key_v[node]
                forest.set_edge_flags(edge_first, edge_second, 0)
                forest.set_edge_flags(edge_second, edge_first, 0)
                self.forests[level + 1].link(
                    edge_first, edge_second, EXACT_LEVEL
                )
                first_root = forest._splay(node)
            while forest.aggregate_flags[first_root] & EDGE_MARK:
                node = forest.search_flag(first_root, EDGE_MARK)
                vertex = forest.key_u[node]
                adjacency = self.non_tree[level]
                while vertex in adjacency:
                    other = next(iter(adjacency[vertex]))
                    if forest.connected(vertex, other):
                        self._erase_non_tree(level, vertex, other)
                        self._add_non_tree(level + 1, vertex, other)
                        continue
                    self._erase_non_tree(level, vertex, other)
                    forest.link(vertex, other, EXACT_LEVEL)
                    replacement = (vertex, other)
                    break
                if replacement is not None:
                    break
                first_root = forest._splay(node)
        return replacement

    def link(self, first, second):
        self._check_vertex(first)
        self._check_vertex(second)
        edge = self._edge(first, second)
        count = self.edge_count.get(edge, 0)
        self.edge_count[edge] = count + 1
        if count or first == second:
            return -1, -1
        forest = self.forests[0]
        if forest.connected(first, second):
            self._add_non_tree(0, first, second)
            return -1, -1
        forest.link(first, second, EXACT_LEVEL)
        self.component_count -= 1
        return edge

    def cut(self, first, second):
        self._check_vertex(first)
        self._check_vertex(second)
        edge = self._edge(first, second)
        count = self.edge_count.get(edge, 0)
        if count == 0:
            return ForestCutQuery((-1, -1), (-1, -1))
        if count > 1:
            self.edge_count[edge] = count - 1
            return ForestCutQuery((-1, -1), (-1, -1))
        del self.edge_count[edge]
        if first == second:
            return ForestCutQuery((-1, -1), (-1, -1))
        forest = self.forests[0]
        if not forest.has_edge(first, second):
            for level in range(self.level_count):
                adjacency = self.non_tree[level]
                if first in adjacency and second in adjacency[first]:
                    self._erase_non_tree(level, first, second)
                    break
            return ForestCutQuery((-1, -1), (-1, -1))
        replacement = self._replace(first, second)
        if replacement is None:
            self.component_count += 1
            replacement = (-1, -1)
        return ForestCutQuery(edge, replacement)

    def connected(self, first, second):
        self._check_vertex(first)
        self._check_vertex(second)
        return self.forests[0].connected(first, second)

    same = connected
    is_connected = connected

    def component_size(self, vertex):
        self._check_vertex(vertex)
        return self.forests[0].component_data(vertex)[1]

    size = component_size


OnlineFullyDynamicConnectivityBySplayEtt = OnlineDynamicConnectivity
