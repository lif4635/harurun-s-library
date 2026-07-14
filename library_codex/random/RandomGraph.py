from dataclasses import dataclass


_MASK64 = (1 << 64) - 1


class Random:
    """SplitMix64-seeded xoshiro256** generator."""

    __slots__ = ("state",)

    def __init__(self, seed=0):
        state = []
        for _ in range(4):
            seed = (seed + 0x9E3779B97F4A7C15) & _MASK64
            value = seed
            value = ((value ^ (value >> 30)) * 0xBF58476D1CE4E5B9) & _MASK64
            value = ((value ^ (value >> 27)) * 0x94D049BB133111EB) & _MASK64
            state.append((value ^ (value >> 31)) & _MASK64)
        self.state = state

    @staticmethod
    def _rotate(value, shift):
        return ((value << shift) | (value >> (64 - shift))) & _MASK64

    def next_u64(self):
        state = self.state
        result = self._rotate(state[1] * 5 & _MASK64, 7) * 9 & _MASK64
        temporary = state[1] << 17 & _MASK64
        state[2] ^= state[0]
        state[3] ^= state[1]
        state[1] ^= state[2]
        state[0] ^= state[3]
        state[2] ^= temporary
        state[3] = self._rotate(state[3], 45)
        return result

    def randrange(self, lower, upper=None):
        if upper is None:
            upper = lower
            lower = 0
        if lower >= upper:
            raise ValueError("empty random range")
        width = upper - lower
        limit = (1 << 64) - ((1 << 64) % width)
        while True:
            value = self.next_u64()
            if value < limit:
                return lower + value % width

    def uniform(self, lower, upper):
        """Uniform integer in the inclusive interval [lower, upper]."""
        return self.randrange(lower, upper + 1)

    def uniform_bool(self):
        return bool(self.next_u64() & 1)

    def uniform01(self):
        return (self.next_u64() >> 11) * (1.0 / (1 << 53))

    def uniform_pair(self, lower, upper):
        if upper - lower < 1:
            raise ValueError("two distinct values are required")
        first = self.uniform(lower, upper)
        second = self.uniform(lower, upper - 1)
        if second >= first:
            second += 1
        return (first, second) if first < second else (second, first)

    def shuffle(self, values):
        for index in range(1, len(values)):
            target = self.randrange(index + 1)
            values[index], values[target] = values[target], values[index]
        return values

    def permutation(self, size):
        return self.shuffle(list(range(size)))

    perm = permutation

    def choice_distinct(self, count, lower, upper):
        if count < 0 or count > upper - lower + 1:
            raise ValueError("invalid sample size")
        if count * 3 < upper - lower + 1:
            result = set()
            while len(result) < count:
                result.add(self.uniform(lower, upper))
            return sorted(result)
        values = list(range(lower, upper + 1))
        self.shuffle(values)
        return sorted(values[:count])

    choice = choice_distinct

    def lower_string(self, length):
        return "".join(chr(self.uniform(97, 122)) for _ in range(length))


@dataclass(frozen=True)
class Edge:
    u: int
    v: int
    weight: int = 1
    index: int = -1

    @property
    def w(self):
        return self.weight

    @property
    def idx(self):
        return self.index


class Graph:
    __slots__ = ("n", "weighted", "edges")

    def __init__(self, vertex_count=0, weighted=False):
        self.n = vertex_count
        self.weighted = weighted
        self.edges = []

    def edges_size(self):
        return len(self.edges)

    def add_directed_edge(self, first, second, weight=1, index=-1):
        self.edges.append(Edge(first, second, weight, index))

    def add_undirected_edge(self, first, second, weight=1, index=-1):
        if first > second:
            first, second = second, first
        self.add_directed_edge(first, second, weight, index)

    def adjacent_list(self, directed=False):
        graph = [[] for _ in range(self.n)]
        for edge in self.edges:
            graph[edge.u].append(edge)
            if not directed:
                graph[edge.v].append(Edge(edge.v, edge.u, edge.weight, edge.index))
        return graph

    def adjacent_matrix(self, directed=False):
        matrix = [[0] * self.n for _ in range(self.n)]
        for edge in self.edges:
            matrix[edge.u][edge.v] = edge.weight
            if not directed:
                matrix[edge.v][edge.u] = edge.weight
        return matrix

    def format_edges(self, zero_indexed=False):
        offset = 0 if zero_indexed else 1
        lines = []
        for edge in self.edges:
            line = f"{edge.u + offset} {edge.v + offset}"
            if self.weighted:
                line += f" {edge.weight}"
            lines.append(line)
        return "\n".join(lines)

    def __str__(self):
        edges = self.format_edges()
        header = f"{self.n} {len(self.edges)}"
        return header + ("\n" + edges if edges else "")


class UndirectedGraphGenerator:
    __slots__ = ("random",)

    def __init__(self, seed=1):
        self.random = Random(seed ^ 1333)

    def set_seed(self, seed):
        self.random = Random(seed ^ 1333)

    def _weight(self, weighted, minimum, maximum):
        return self.random.uniform(minimum, maximum) if weighted else 1

    def _add(self, graph, first, second, weighted, minimum, maximum):
        graph.add_undirected_edge(
            first, second, self._weight(weighted, minimum, maximum)
        )

    def tree(self, n, weighted=False, weight_min=1, weight_max=1):
        graph = Graph(n, weighted)
        if n <= 1:
            return graph
        code = [self.random.randrange(n) for _ in range(n - 2)]
        degree = [1] * n
        for vertex in code:
            degree[vertex] += 1
        leaves = [vertex for vertex in range(n) if degree[vertex] == 1]
        import heapq
        heapq.heapify(leaves)
        for vertex in code:
            leaf = heapq.heappop(leaves)
            self._add(graph, vertex, leaf, weighted, weight_min, weight_max)
            degree[vertex] -= 1
            if degree[vertex] == 1:
                heapq.heappush(leaves, vertex)
        self._add(graph, leaves[0], leaves[1], weighted, weight_min, weight_max)
        return graph

    def path(self, n, weighted=False, weight_min=1, weight_max=1):
        order = self.random.permutation(n)
        graph = Graph(n, weighted)
        for index in range(n - 1):
            self._add(graph, order[index], order[index + 1],
                      weighted, weight_min, weight_max)
        return graph

    def star(self, n, weighted=False, weight_min=1, weight_max=1):
        order = self.random.permutation(n)
        graph = Graph(n, weighted)
        for index in range(1, n):
            self._add(graph, order[0], order[index], weighted, weight_min, weight_max)
        return graph

    def complete(self, n, weighted=False, weight_min=1, weight_max=1):
        graph = Graph(n, weighted)
        for first in range(n):
            for second in range(first + 1, n):
                self._add(graph, first, second, weighted, weight_min, weight_max)
        return graph

    perfect = complete

    def simple(self, n, weighted=False, weight_min=1, weight_max=1):
        graph = Graph(n, weighted)
        for first in range(n):
            for second in range(first + 1, n):
                if self.random.uniform_bool():
                    self._add(graph, first, second, weighted, weight_min, weight_max)
        return graph

    def namori(self, n, weighted=False, weight_min=1, weight_max=1):
        graph = Graph(n, weighted)
        if n < 2:
            return graph
        self._add(graph, 0, self.random.randrange(1, n),
                  weighted, weight_min, weight_max)
        for vertex in range(1, n):
            self._add(graph, vertex, self.random.randrange(vertex),
                      weighted, weight_min, weight_max)
        return graph

    def simple_sparse(self, n, weighted=False, weight_min=1, weight_max=1):
        graph = Graph(n, weighted)
        if n == 0:
            return graph
        count = self.random.randrange(n)
        possible = [(first, second) for first in range(n)
                    for second in range(first + 1, n)]
        self.random.shuffle(possible)
        for first, second in possible[:count]:
            self._add(graph, first, second, weighted, weight_min, weight_max)
        return graph

    def test(self, n, is_tree=True, weighted=False, weight_min=1, weight_max=1):
        functions = (self.tree, self.path, self.star) if is_tree else (
            self.tree, self.path, self.star, self.complete, self.simple,
            self.namori, self.simple_sparse,
        )
        function = functions[self.random.randrange(len(functions))]
        return function(n, weighted, weight_min, weight_max)


undirected = UndirectedGraphGenerator()
