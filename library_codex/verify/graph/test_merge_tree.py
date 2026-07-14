import random

from library_codex.graph.MergeTree import MergeTree


def test_merge_tree_ranges_against_live_components():
    rng = random.Random(52)
    for n in range(1, 60):
        merges = [(rng.randrange(n), rng.randrange(n)) for _ in range(100)]
        tree = MergeTree(n, merges)
        values = [rng.randrange(1000) for _ in range(n)]
        assert tree.restore(tree.arrange(values)) == values
        components = [{vertex} for vertex in range(n)]
        representative = list(range(n))
        for first, second in merges:
            left = representative[first]
            right = representative[second]
            if left != right:
                components[left] |= components[right]
                for vertex in components[right]:
                    representative[vertex] = left
                components[right] = set()
            tree.unite(first, second)
            for vertex in range(n):
                begin, end = tree.component_range(vertex)
                assert set(tree.order[begin:end]) == components[representative[vertex]]
