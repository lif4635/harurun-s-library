from collections import deque

from library_codex.random.Random import Random
from library_codex.random.RandomGraph import Graph, UndirectedGraphGenerator


def test_random_reproducibility_and_ranges():
    first = Random(12345)
    second = Random(12345)
    assert [first.next_u64() for _ in range(1000)] == [
        second.next_u64() for _ in range(1000)
    ]
    random = Random(9)
    assert all(-10 <= random.randrange(-10, 20) < 20 for _ in range(10000))
    permutation = random.permutation(1000)
    assert sorted(permutation) == list(range(1000))
    sample = random.sample_range(100, -500, 500)
    assert sample == sorted(sample) and len(set(sample)) == 100


def test_test_case_helpers():
    random = Random(81)
    array = random.array(50, -3, 7)
    assert len(array) == 50 and all(-3 <= value <= 7 for value in array)
    distinct = random.array(20, -30, 30, distinct=True)
    assert len(distinct) == len(set(distinct)) == 20
    ordered = random.array(100, -5, 5, sort_result=True)
    assert ordered == sorted(ordered)
    bits = random.bits(100, ones=37)
    assert len(bits) == 100 and sum(bits) == 37 and set(bits) <= {0, 1}
    matrix = random.matrix(7, 11, -2, 4)
    assert len(matrix) == 7
    assert all(len(row) == 11 for row in matrix)
    assert all(-2 <= value <= 4 for row in matrix for value in row)
    assert set(random.string(200, "abc")) <= set("abc")
    assert sorted(random.sample(list(range(50)), 20)) != list(range(20))
    for allow_empty in (False, True):
        intervals = random.intervals(100, -10, 30, allow_empty)
        assert all(
            -10 <= left <= right <= 30 and (allow_empty or left < right)
            for left, right in intervals
        )
    for total in range(20):
        for parts in range(1, 8):
            weak = random.composition(total, parts)
            assert len(weak) == parts and sum(weak) == total and min(weak) >= 0
            if total >= parts:
                positive = random.composition(total, parts, True)
                assert len(positive) == parts and sum(positive) == total
                assert min(positive) >= 1


def test_random_balanced_brackets_and_monge_matrices():
    first = Random(192837)
    second = Random(192837)
    assert [first.brackets(30) for _ in range(100)] == [
        second.brackets(30) for _ in range(100)
    ]
    random = Random(564738)
    for pairs in range(100):
        brackets = random.brackets(pairs)
        assert len(brackets) == 2 * pairs
        balance = 0
        for bracket in brackets:
            balance += 1 if bracket == "(" else -1
            assert balance >= 0
        assert balance == 0
    assert random.brackets(3, "[", "]").count("[") == 3

    for rows in range(20):
        for columns in range(20):
            matrix = random.monge(rows, columns, 20, 100)
            assert len(matrix) == rows
            assert all(len(row) == columns for row in matrix)
            for first_row in range(rows):
                for second_row in range(first_row + 1, rows):
                    for first_column in range(columns):
                        for second_column in range(first_column + 1, columns):
                            assert (
                                matrix[first_row][first_column]
                                + matrix[second_row][second_column]
                                <= matrix[first_row][second_column]
                                + matrix[second_row][first_column]
                            )


def _is_connected(graph):
    if graph.n == 0:
        return True
    adjacency = graph.to_adjacency_list()
    seen = [False] * graph.n
    queue = deque([0])
    seen[0] = True
    while queue:
        vertex = queue.popleft()
        for edge in adjacency[vertex]:
            if not seen[edge.v]:
                seen[edge.v] = True
                queue.append(edge.v)
    return all(seen)


def _assert_simple(graph):
    pairs = [(edge.u, edge.v) for edge in graph.edges]
    assert all(0 <= first < second < graph.n for first, second in pairs)
    assert len(pairs) == len(set(pairs))


def _component_count(graph):
    adjacency = graph.to_adjacency_list()
    seen = [False] * graph.n
    count = 0
    for start in range(graph.n):
        if seen[start]:
            continue
        count += 1
        seen[start] = True
        queue = deque([start])
        while queue:
            vertex = queue.popleft()
            for edge in adjacency[vertex]:
                if not seen[edge.v]:
                    seen[edge.v] = True
                    queue.append(edge.v)
    return count


def test_graph_and_generators():
    generator = UndirectedGraphGenerator(77)
    for n in range(70):
        tree = generator.tree(n, True, -20, 20)
        assert tree.edge_count() == max(0, n - 1)
        assert all(-20 <= edge.weight <= 20 for edge in tree.edges)
        assert _is_connected(tree)
        path = generator.path(n)
        assert path.edge_count() == max(0, n - 1)
        star = generator.star(n)
        assert star.edge_count() == max(0, n - 1)
        components = 0 if n == 0 else max(1, n // 5)
        forest = generator.forest(n, components)
        assert forest.edge_count() == n - components
        assert _component_count(forest) == components
        _assert_simple(forest)
        if n >= 3:
            cycle = generator.cycle(n)
            assert cycle.edge_count() == n
            assert _is_connected(cycle)
            _assert_simple(cycle)
        complete = generator.complete(n)
        assert complete.edge_count() == n * (n - 1) // 2

        maximum = n * (n - 1) // 2
        edge_count = min(maximum, n + 7)
        simple = generator.simple(n, edge_count)
        assert simple.edge_count() == edge_count
        _assert_simple(simple)
        if n:
            connected_count = min(maximum, max(n - 1, n + 5))
            connected = generator.connected(n, connected_count)
            assert connected.edge_count() == connected_count
            _assert_simple(connected)
            assert _is_connected(connected)
    bipartite = generator.bipartite(17, 13, 80, True, -9, 9)
    assert bipartite.n == 30 and bipartite.edge_count() == 80
    _assert_simple(bipartite)
    assert all(edge.u < 17 <= edge.v for edge in bipartite.edges)
    assert all(-9 <= edge.weight <= 9 for edge in bipartite.edges)
    graph = Graph(3, True)
    graph.add_undirected_edge(2, 0, 7)
    graph.add_directed_edge(1, 2, 9)
    assert graph.to_adjacency_matrix(True) == [
        [0, 0, 7],
        [0, 0, 9],
        [0, 0, 0],
    ]


def test_no_redundant_random_alias_methods():
    assert not hasattr(Random, "integers")
    assert not hasattr(Random, "perm")
    assert not hasattr(Random, "choice_distinct")
    assert not hasattr(UndirectedGraphGenerator, "perfect")
