"""Matching and Boolean-constraint utilities without recursive DFS."""

from graph.BipartiteMatching import BipartiteMatching
from graph.StronglyConnectedComponents import StronglyConnectedComponents


class GeneralMatching:
    """Edmonds blossom algorithm for maximum cardinality matching."""

    __slots__ = ("n", "graph", "mate", "matching_size")

    def __init__(self, graph):
        self.n = len(graph)
        self.graph = [list(dict.fromkeys(v for v in row if v != u))
                      for u, row in enumerate(graph)]
        self.mate = [-1] * self.n
        self.matching_size = 0
        self._solve()

    def _solve(self):
        n = self.n
        graph = self.graph
        mate = self.mate
        parent = [-1] * n
        base = list(range(n))
        used = [False] * n
        blossom = [False] * n

        def lca(first, second):
            path = [False] * n
            while True:
                first = base[first]
                path[first] = True
                if mate[first] == -1:
                    break
                first = parent[mate[first]]
            while True:
                second = base[second]
                if path[second]:
                    return second
                second = parent[mate[second]]

        def mark_path(vertex, common, child):
            while base[vertex] != common:
                blossom[base[vertex]] = True
                blossom[base[mate[vertex]]] = True
                parent[vertex] = child
                child = mate[vertex]
                vertex = parent[mate[vertex]]

        for root in range(n):
            if mate[root] != -1:
                continue
            for i in range(n):
                parent[i] = -1
                base[i] = i
                used[i] = False
            used[root] = True
            queue = [root]
            finish = -1
            head = 0
            while head < len(queue) and finish == -1:
                vertex = queue[head]
                head += 1
                for to in graph[vertex]:
                    if base[vertex] == base[to] or mate[vertex] == to:
                        continue
                    if to == root or (mate[to] != -1
                                      and parent[mate[to]] != -1):
                        common = lca(vertex, to)
                        for i in range(n):
                            blossom[i] = False
                        mark_path(vertex, common, to)
                        mark_path(to, common, vertex)
                        for i in range(n):
                            if blossom[base[i]]:
                                base[i] = common
                                if not used[i]:
                                    used[i] = True
                                    queue.append(i)
                    elif parent[to] == -1:
                        parent[to] = vertex
                        if mate[to] == -1:
                            finish = to
                            break
                        nxt = mate[to]
                        if not used[nxt]:
                            used[nxt] = True
                            queue.append(nxt)
            if finish == -1:
                continue
            self.matching_size += 1
            vertex = finish
            while vertex != -1:
                previous = parent[vertex]
                nxt = mate[previous] if previous != -1 else -1
                mate[vertex] = previous
                if previous != -1:
                    mate[previous] = vertex
                vertex = nxt

    def pairs(self):
        return [(v, to) for v, to in enumerate(self.mate) if v < to]

    maximum_matching = pairs


def maximum_general_matching(graph):
    solver = GeneralMatching(graph)
    return solver.matching_size, solver.mate


class TwoSAT:
    """2-SAT with the node convention ``2*v=false, 2*v+1=true``."""

    __slots__ = ("n", "graph", "answer")

    def __init__(self, n):
        self.n = n
        self.graph = [[] for _ in range(n << 1)]
        self.answer = None

    @staticmethod
    def literal(variable, value=True):
        return (variable << 1) | bool(value)

    def add_implication_literal(self, source, target):
        self.graph[source].append(target)
        self.graph[target ^ 1].append(source ^ 1)

    def add_clause_literal(self, first, second):
        self.graph[first ^ 1].append(second)
        self.graph[second ^ 1].append(first)

    def add_clause(self, first_variable, first_value,
                   second_variable, second_value):
        self.add_clause_literal(
            self.literal(first_variable, first_value),
            self.literal(second_variable, second_value),
        )

    def set_value(self, variable, value=True):
        literal = self.literal(variable, value)
        self.graph[literal ^ 1].append(literal)

    def add_xor(self, first, second):
        self.add_clause(first, True, second, True)
        self.add_clause(first, False, second, False)

    def add_equal(self, first, second):
        self.add_clause(first, False, second, True)
        self.add_clause(first, True, second, False)

    def solve(self):
        scc = StronglyConnectedComponents(self.graph)
        component = scc.component
        answer = [False] * self.n
        for variable in range(self.n):
            false = variable << 1
            if component[false] == component[false | 1]:
                self.answer = None
                return None
            answer[variable] = component[false] < component[false | 1]
        self.answer = answer
        return answer

    satisfiable = solve


class DynamicBipartiteGraph:
    """Add-only bipartiteness with parity Union-Find."""

    __slots__ = (
        "n", "parent", "parity", "count0", "count1", "bipartite",
        "maximum_side_sum"
    )

    def __init__(self, n):
        self.n = n
        self.parent = [-1] * n
        self.parity = [0] * n
        self.count0 = [1] * n
        self.count1 = [0] * n
        self.bipartite = True
        self.maximum_side_sum = n

    def find(self, vertex):
        root = vertex
        value = 0
        while self.parent[root] >= 0:
            value ^= self.parity[root]
            root = self.parent[root]
        while vertex != root:
            nxt = self.parent[vertex]
            edge = self.parity[vertex]
            self.parent[vertex] = root
            self.parity[vertex] = value
            value ^= edge
            vertex = nxt
        return root

    def color(self, vertex):
        self.find(vertex)
        return self.parity[vertex]

    def can_add_edge(self, first, second):
        if not self.bipartite:
            return False
        root_first = self.find(first)
        root_second = self.find(second)
        return (root_first != root_second
                or (self.parity[first] ^ self.parity[second]) == 1)

    can_unite = can_add_edge

    def add_edge(self, first, second):
        if not self.bipartite:
            return False
        root_first = self.find(first)
        root_second = self.find(second)
        first_color = self.parity[first]
        second_color = self.parity[second]
        if root_first == root_second:
            if first_color == second_color:
                self.bipartite = False
                self.maximum_side_sum = -1
                return False
            return True
        self.maximum_side_sum -= max(
            self.count0[root_first], self.count1[root_first]
        ) + max(self.count0[root_second], self.count1[root_second])
        relation = first_color ^ second_color ^ 1
        if self.parent[root_first] > self.parent[root_second]:
            root_first, root_second = root_second, root_first
        # Recompute orientation if union-by-size swapped the roots.
        self.parent[root_first] += self.parent[root_second]
        self.parent[root_second] = root_first
        self.parity[root_second] = relation
        if relation:
            self.count0[root_first] += self.count1[root_second]
            self.count1[root_first] += self.count0[root_second]
        else:
            self.count0[root_first] += self.count0[root_second]
            self.count1[root_first] += self.count1[root_second]
        self.maximum_side_sum += max(
            self.count0[root_first], self.count1[root_first]
        )
        return True

    unite = add_edge

    def is_bipartite(self):
        return self.bipartite


def dag_minimum_path_cover(graph):
    """Return a minimum vertex-disjoint path cover of a DAG.

    The caller is responsible for the DAG precondition.  The result is a list
    of vertex lists and has size N minus the maximum bipartite matching size.
    """
    n = len(graph)
    matching = BipartiteMatching(n, n)
    for source, row in enumerate(graph):
        for target in row:
            matching.add_edge(source, target)
    matching.solve()
    successor = matching.match_left
    predecessor = matching.match_right
    paths = []
    used = [False] * n
    for start in range(n):
        if predecessor[start] != -1:
            continue
        path = []
        vertex = start
        while vertex != -1 and not used[vertex]:
            used[vertex] = True
            path.append(vertex)
            vertex = successor[vertex]
        paths.append(path)
    for start in range(n):
        if not used[start]:
            path = []
            vertex = start
            while vertex != -1 and not used[vertex]:
                used[vertex] = True
                path.append(vertex)
                vertex = successor[vertex]
            paths.append(path)
    return paths
