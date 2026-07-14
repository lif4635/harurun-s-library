"""Implicit graph builders for ranges and multidimensional grids."""

from collections import deque
from heapq import heappop, heappush


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


class DimensionExpandedGraph:
    """Flattened rectangular grid with optional extra non-grid vertices."""

    __slots__ = ("shape", "dimension", "strides", "grid_size", "extra")

    def __init__(self, *shape, extra=0):
        if not shape or any(length <= 0 for length in shape):
            raise ValueError("all dimensions must be positive")
        self.shape = tuple(shape)
        self.dimension = len(shape)
        strides = [1] * len(shape)
        for i in range(len(shape) - 2, -1, -1):
            strides[i] = strides[i + 1] * shape[i + 1]
        self.strides = strides
        self.grid_size = shape[0] * strides[0]
        self.extra = extra

    def __len__(self):
        return self.grid_size + self.extra

    def valid(self, coordinate):
        return (len(coordinate) == self.dimension
                and all(0 <= value < size
                        for value, size in zip(coordinate, self.shape)))

    ok = valid

    def id(self, coordinate):
        if not self.valid(coordinate):
            raise IndexError("coordinate out of grid")
        return sum(value * stride
                   for value, stride in zip(coordinate, self.strides))

    def coordinate(self, vertex):
        if not 0 <= vertex < self.grid_size:
            raise IndexError("vertex is not a grid cell")
        result = [0] * self.dimension
        for i, stride in enumerate(self.strides):
            result[i], vertex = divmod(vertex, stride)
        return tuple(result)

    def extra_id(self, index):
        if not 0 <= index < self.extra:
            raise IndexError("extra vertex out of range")
        return self.grid_size + index

    def neighbors(self, coordinate):
        coordinate = list(coordinate)
        result = []
        for axis in range(self.dimension):
            value = coordinate[axis]
            if value:
                coordinate[axis] = value - 1
                result.append(tuple(coordinate))
            if value + 1 < self.shape[axis]:
                coordinate[axis] = value + 1
                result.append(tuple(coordinate))
            coordinate[axis] = value
        return result

    near = neighbors

    def bfs(self, start, transitions=None):
        """Unweighted distances; transitions(id) defaults to grid neighbors."""
        start = self.id(start) if not isinstance(start, int) else start
        distance = [-1] * len(self)
        distance[start] = 0
        queue = [start]
        for vertex in queue:
            if transitions is None:
                adjacent = (self.id(x) for x in self.neighbors(
                    self.coordinate(vertex)
                )) if vertex < self.grid_size else ()
            else:
                adjacent = transitions(vertex)
            for to in adjacent:
                if distance[to] == -1:
                    distance[to] = distance[vertex] + 1
                    queue.append(to)
        return distance

    def bfs01(self, start, transitions):
        start = self.id(start) if not isinstance(start, int) else start
        inf = float("inf")
        distance = [inf] * len(self)
        distance[start] = 0
        queue = deque([start])
        while queue:
            vertex = queue.popleft()
            dist = distance[vertex]
            for to, weight in transitions(vertex):
                nxt = dist + weight
                if nxt < distance[to]:
                    distance[to] = nxt
                    if weight:
                        queue.append(to)
                    else:
                        queue.appendleft(to)
        return distance

    def dijkstra(self, start, transitions):
        start = self.id(start) if not isinstance(start, int) else start
        inf = float("inf")
        distance = [inf] * len(self)
        distance[start] = 0
        heap = [(0, start)]
        while heap:
            dist, vertex = heappop(heap)
            if distance[vertex] != dist:
                continue
            for to, weight in transitions(vertex):
                nxt = dist + weight
                if nxt < distance[to]:
                    distance[to] = nxt
                    heappush(heap, (nxt, to))
        return distance


def reverse_graph(graph):
    reverse = [[] for _ in graph]
    for source, row in enumerate(graph):
        for entry in row:
            if isinstance(entry, int):
                reverse[entry].append(source)
            else:
                target = entry[0]
                reverse[target].append((source,) + tuple(entry[1:]))
    return reverse


def grid_to_graph(grid, passable=lambda value: value != "#"):
    """Return a 4-neighbor adjacency list and coordinate/ID helpers."""
    height = len(grid)
    width = len(grid[0]) if height else 0
    graph = [[] for _ in range(height * width)]
    for row in range(height):
        for column in range(width):
            if not passable(grid[row][column]):
                continue
            vertex = row * width + column
            if row and passable(grid[row - 1][column]):
                graph[vertex].append(vertex - width)
            if row + 1 < height and passable(grid[row + 1][column]):
                graph[vertex].append(vertex + width)
            if column and passable(grid[row][column - 1]):
                graph[vertex].append(vertex - 1)
            if column + 1 < width and passable(grid[row][column + 1]):
                graph[vertex].append(vertex + 1)
    return (graph, (lambda row, column: row * width + column),
            (lambda vertex: divmod(vertex, width)))
