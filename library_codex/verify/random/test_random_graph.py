from library_codex.random.RandomGraph import Graph, Random, UndirectedGraphGenerator


def test_random_reproducibility_and_ranges():
    first = Random(12345)
    second = Random(12345)
    assert [first.next_u64() for _ in range(1000)] == [second.next_u64() for _ in range(1000)]
    random = Random(9)
    assert all(-10 <= random.randrange(-10, 20) < 20 for _ in range(10000))
    permutation = random.permutation(1000)
    assert sorted(permutation) == list(range(1000))
    assert len(set(random.choice_distinct(100, -500, 500))) == 100


def test_graph_and_generators():
    generator = UndirectedGraphGenerator(77)
    for n in range(100):
        tree = generator.tree(n, True, -20, 20)
        assert tree.edges_size() == max(0, n - 1)
        assert all(-20 <= edge.weight <= 20 for edge in tree.edges)
        path = generator.path(n)
        assert path.edges_size() == max(0, n - 1)
        star = generator.star(n)
        assert star.edges_size() == max(0, n - 1)
        complete = generator.complete(n)
        assert complete.edges_size() == n * (n - 1) // 2
        sparse = generator.simple_sparse(n)
        assert len({(edge.u, edge.v) for edge in sparse.edges}) == sparse.edges_size()
    graph = Graph(3, True)
    graph.add_undirected_edge(2, 0, 7)
    graph.add_directed_edge(1, 2, 9)
    assert graph.adjacent_matrix(True) == [[0, 0, 7], [0, 0, 9], [0, 0, 0]]
