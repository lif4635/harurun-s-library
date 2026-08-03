"""座標状態を追加次元へ展開したグラフを構築する。"""

from collections import deque

from heapq import heappop, heappush

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

