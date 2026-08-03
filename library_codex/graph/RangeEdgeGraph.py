"""頂点から区間・区間から頂点への辺を対数個の補助辺で追加する。"""

class RangeEdgeGraph:
    """Directed weighted graph supporting point/range endpoint edges.

    Original vertices keep IDs ``0..n-1``.  The initial segment-DAG uses
    exactly ``3*n-2`` vertices for positive n.  A range-to-range edge allocates
    two more vertices so that its cost is paid exactly once.
    """

    __slots__ = (
        "n", "zero", "graph", "root", "left_bound", "right_bound",
        "left_child", "right_child", "in_id", "out_id"
    )

    def __init__(self, n, zero=0):
        if n < 0:
            raise ValueError("n must be nonnegative")
        self.n = n
        self.zero = zero
        if n == 0:
            self.graph = []
            self.root = -1
            self.left_bound = []
            self.right_bound = []
            self.left_child = []
            self.right_child = []
            self.in_id = []
            self.out_id = []
            return
        self.root = 0
        left_bound = [0]
        right_bound = [n]
        left_child = [-1]
        right_child = [-1]
        in_id = [-1]
        out_id = [-1]
        next_vertex = n
        stack = [0]
        while stack:
            node = stack.pop()
            left = left_bound[node]
            right = right_bound[node]
            if right - left == 1:
                in_id[node] = out_id[node] = left
                continue
            in_id[node] = next_vertex
            out_id[node] = next_vertex + 1
            next_vertex += 2
            middle = (left + right) >> 1
            lc = len(left_bound)
            rc = lc + 1
            left_child[node] = lc
            right_child[node] = rc
            left_bound.extend((left, middle))
            right_bound.extend((middle, right))
            left_child.extend((-1, -1))
            right_child.extend((-1, -1))
            in_id.extend((-1, -1))
            out_id.extend((-1, -1))
            stack.append(rc)
            stack.append(lc)
        graph = [[] for _ in range(next_vertex)]
        for node in range(len(left_bound)):
            lc = left_child[node]
            if lc == -1:
                continue
            rc = right_child[node]
            graph[in_id[node]].append((in_id[lc], zero))
            graph[in_id[node]].append((in_id[rc], zero))
            graph[out_id[lc]].append((out_id[node], zero))
            graph[out_id[rc]].append((out_id[node], zero))
        self.graph = graph
        self.left_bound = left_bound
        self.right_bound = right_bound
        self.left_child = left_child
        self.right_child = right_child
        self.in_id = in_id
        self.out_id = out_id

    def __len__(self):
        return len(self.graph)

    def _validate_range(self, left, right):
        if not 0 <= left <= right <= self.n:
            raise IndexError("invalid half-open range")

    def _validate_vertex(self, vertex):
        if not 0 <= vertex < self.n:
            raise IndexError("original vertex out of range")

    def _cover(self, left, right, ids):
        if left == right:
            return []
        result = []
        stack = [self.root]
        while stack:
            node = stack.pop()
            nl = self.left_bound[node]
            nr = self.right_bound[node]
            if right <= nl or nr <= left:
                continue
            if left <= nl and nr <= right:
                result.append(ids[node])
            else:
                stack.append(self.right_child[node])
                stack.append(self.left_child[node])
        return result

    def _new_vertex(self):
        vertex = len(self.graph)
        self.graph.append([])
        return vertex

    def add_point_to_point(self, source, target, cost):
        self._validate_vertex(source)
        self._validate_vertex(target)
        self.graph[source].append((target, cost))

    def add_point_to_range(self, source, left, right, cost):
        self._validate_vertex(source)
        self._validate_range(left, right)
        for target in self._cover(left, right, self.in_id):
            self.graph[source].append((target, cost))

    def add_range_to_point(self, left, right, target, cost):
        self._validate_range(left, right)
        self._validate_vertex(target)
        for source in self._cover(left, right, self.out_id):
            self.graph[source].append((target, cost))

    def add_range_to_range(self, from_left, from_right,
                           to_left, to_right, cost):
        self._validate_range(from_left, from_right)
        self._validate_range(to_left, to_right)
        if from_left == from_right or to_left == to_right:
            return
        bridge_in = self._new_vertex()
        bridge_out = self._new_vertex()
        for source in self._cover(from_left, from_right, self.out_id):
            self.graph[source].append((bridge_in, self.zero))
        self.graph[bridge_in].append((bridge_out, cost))
        for target in self._cover(to_left, to_right, self.in_id):
            self.graph[bridge_out].append((target, self.zero))

    def add_edge(self, source, target, cost):
        self.add_point_to_point(source, target, cost)

