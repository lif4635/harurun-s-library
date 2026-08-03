"""Containers and generators for random undirected graph test cases."""

from dataclasses import dataclass

from library_codex.random.Random import Random


@dataclass(frozen=True)
class Edge:
    """One stored edge using 0-indexed endpoints."""

    u: int
    v: int
    weight: int = 1
    index: int = -1


class Graph:
    """A compact edge-list graph that can be printed as contest input."""

    __slots__ = ("n", "weighted", "edges")

    def __init__(self, vertex_count=0, weighted=False):
        self.n = vertex_count
        self.weighted = weighted
        self.edges = []

    def edge_count(self):
        """Return the number of stored edges."""
        return len(self.edges)

    def add_directed_edge(self, first, second, weight=1, index=-1):
        """Append one directed edge and return its edge-list index."""
        self.edges.append(Edge(first, second, weight, index))
        return len(self.edges) - 1

    def add_undirected_edge(self, first, second, weight=1, index=-1):
        """Append one undirected edge with its smaller endpoint first."""
        if first > second:
            first, second = second, first
        self.edges.append(Edge(first, second, weight, index))
        return len(self.edges) - 1

    def to_adjacency_list(self, directed=False):
        """Return adjacency lists containing directed Edge records."""
        graph = [[] for _ in range(self.n)]
        for edge in self.edges:
            graph[edge.u].append(edge)
            if not directed:
                graph[edge.v].append(Edge(edge.v, edge.u, edge.weight, edge.index))
        return graph

    def to_adjacency_matrix(self, directed=False):
        """Return an n-by-n matrix whose entries are edge weights or zero."""
        matrix = [[0] * self.n for _ in range(self.n)]
        for edge in self.edges:
            matrix[edge.u][edge.v] = edge.weight
            if not directed:
                matrix[edge.v][edge.u] = edge.weight
        return matrix

    def format_edges(self, zero_indexed=False):
        """Return newline-separated edge rows, with weights when enabled."""
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
    """Generate reproducible simple undirected graph families."""

    __slots__ = ("random",)

    def __init__(self, seed=1):
        self.random = Random(seed)

    def set_seed(self, seed):
        """Reset the generator and return self."""
        self.random = Random(seed)
        return self

    def _weight(self, weighted, minimum, maximum):
        return self.random.uniform(minimum, maximum) if weighted else 1

    def _add(self, graph, first, second, weighted, minimum, maximum):
        graph.add_undirected_edge(
            first,
            second,
            self._weight(weighted, minimum, maximum),
        )

    @staticmethod
    def _edge_from_index(n, edge_index):
        """Map [0, nC2) to lexicographically ordered endpoint pairs."""
        low = 0
        high = n - 1
        while low + 1 < high:
            middle = (low + high) // 2
            skipped = middle * (2 * n - middle - 1) // 2
            if skipped <= edge_index:
                low = middle
            else:
                high = middle
        skipped = low * (2 * n - low - 1) // 2
        return low, low + 1 + edge_index - skipped

    def tree(self, n, weighted=False, weight_min=1, weight_max=1):
        """Return a uniformly random labelled tree using a Prüfer code."""
        if n < 0:
            raise ValueError("n must be nonnegative")
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
        self.random.shuffle(graph.edges)
        return graph

    def path(self, n, weighted=False, weight_min=1, weight_max=1):
        """Return a path with randomly permuted vertex labels."""
        order = self.random.permutation(n)
        graph = Graph(n, weighted)
        for index in range(n - 1):
            self._add(
                graph,
                order[index],
                order[index + 1],
                weighted,
                weight_min,
                weight_max,
            )
        return graph

    def star(self, n, weighted=False, weight_min=1, weight_max=1):
        """Return a star with a uniformly random centre vertex."""
        order = self.random.permutation(n)
        graph = Graph(n, weighted)
        for index in range(1, n):
            self._add(
                graph,
                order[0],
                order[index],
                weighted,
                weight_min,
                weight_max,
            )
        return graph

    def cycle(self, n, weighted=False, weight_min=1, weight_max=1):
        """Return a simple cycle with randomly permuted vertex labels."""
        if n < 3:
            raise ValueError("a simple cycle needs at least 3 vertices")
        order = self.random.permutation(n)
        graph = Graph(n, weighted)
        for index in range(n):
            self._add(
                graph,
                order[index],
                order[(index + 1) % n],
                weighted,
                weight_min,
                weight_max,
            )
        return graph

    def forest(
        self,
        n,
        components,
        weighted=False,
        weight_min=1,
        weight_max=1,
    ):
        """Return a random forest with exactly the requested component count."""
        if n < 0 or components < 0:
            raise ValueError("n and components must be nonnegative")
        if (n == 0 and components != 0) or (n > 0 and not 1 <= components <= n):
            raise ValueError("components must be zero only for n=0, otherwise 1..n")
        graph = Graph(n, weighted)
        if n == 0:
            return graph
        order = self.random.permutation(n)
        sizes = self.random.composition(n, components, positive=True)
        offset = 0
        for size in sizes:
            block = order[offset:offset + size]
            for index in range(1, size):
                parent = self.random.randrange(index)
                self._add(
                    graph,
                    block[parent],
                    block[index],
                    weighted,
                    weight_min,
                    weight_max,
                )
            offset += size
        self.random.shuffle(graph.edges)
        return graph

    def complete(self, n, weighted=False, weight_min=1, weight_max=1):
        """Return the complete simple graph K_n."""
        graph = Graph(n, weighted)
        for first in range(n):
            for second in range(first + 1, n):
                self._add(graph, first, second, weighted, weight_min, weight_max)
        return graph

    def simple(self, n, edge_count, weighted=False, weight_min=1, weight_max=1):
        """Return a uniformly sampled simple graph with exactly edge_count edges."""
        maximum = n * (n - 1) // 2
        if n < 0 or not 0 <= edge_count <= maximum:
            raise ValueError("edge_count is outside the simple-graph range")
        selected = self.random.sample_range(edge_count, 0, maximum - 1, False)
        graph = Graph(n, weighted)
        for edge_index in selected:
            first, second = self._edge_from_index(n, edge_index)
            self._add(graph, first, second, weighted, weight_min, weight_max)
        return graph

    def connected(self, n, edge_count, weighted=False, weight_min=1, weight_max=1):
        """Return a connected simple graph with exactly edge_count edges."""
        minimum = max(0, n - 1)
        maximum = n * (n - 1) // 2
        if n < 0 or not minimum <= edge_count <= maximum:
            raise ValueError("a connected graph needs n-1 <= edge_count <= nC2")
        graph = self.tree(n, weighted, weight_min, weight_max)
        used = {(edge.u, edge.v) for edge in graph.edges}
        missing = edge_count - len(used)
        if missing == 0:
            return graph
        available = [
            (first, second)
            for first in range(n)
            for second in range(first + 1, n)
            if (first, second) not in used
        ]
        for first, second in self.random.sample(available, missing):
            self._add(graph, first, second, weighted, weight_min, weight_max)
        self.random.shuffle(graph.edges)
        return graph

    def bipartite(
        self,
        left_size,
        right_size,
        edge_count,
        weighted=False,
        weight_min=1,
        weight_max=1,
    ):
        """Return a simple bipartite graph with an exact number of edges."""
        maximum = left_size * right_size
        if left_size < 0 or right_size < 0 or not 0 <= edge_count <= maximum:
            raise ValueError("edge_count is outside the bipartite-graph range")
        graph = Graph(left_size + right_size, weighted)
        selected = self.random.sample_range(edge_count, 0, maximum - 1, False)
        for edge_index in selected:
            first = edge_index // right_size
            second = left_size + edge_index % right_size
            self._add(graph, first, second, weighted, weight_min, weight_max)
        return graph

    def erdos_renyi(
        self,
        n,
        probability=0.5,
        weighted=False,
        weight_min=1,
        weight_max=1,
    ):
        """Include each possible edge independently with the given probability."""
        if n < 0 or not 0.0 <= probability <= 1.0:
            raise ValueError("probability must be in [0, 1]")
        graph = Graph(n, weighted)
        for first in range(n):
            for second in range(first + 1, n):
                if self.random.uniform01() < probability:
                    self._add(graph, first, second, weighted, weight_min, weight_max)
        return graph

    def unicyclic(self, n, weighted=False, weight_min=1, weight_max=1):
        """Return a connected simple graph with exactly one cycle."""
        if n < 3:
            raise ValueError("a simple unicyclic graph needs at least 3 vertices")
        return self.connected(n, n, weighted, weight_min, weight_max)
