import random
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[3]))

from library_codex.data_structure.RollbackUnionFind import RollbackUnionFind


def test_basic_rollback_and_snapshot():
    uf = RollbackUnionFind(6)
    assert uf.component_count == 6
    assert uf.merge(0, 1)
    state = uf.snapshot()
    assert state == 1
    assert uf.unite(1, 2)
    assert not uf.union(0, 2)
    assert uf.size(0) == 3
    assert uf.count() == 4
    uf.undo()
    assert uf.size(0) == 3
    uf.rollback()
    assert uf.same(0, 1) and not uf.same(0, 2)
    assert uf.component_count == 5
    uf.rollback(0)
    assert uf.snapshot_state == 0
    uf.rollback()
    assert uf.groups() == [[0], [1], [2], [3], [4], [5]]


def test_component_values():
    uf = RollbackUnionFind(4, [2, 3, 5, 7])
    root_state = uf.get_state()
    uf.merge(0, 1)
    assert uf.component_sum(0) == 5
    value_state = uf.get_state()
    assert uf.add_value(1, 11) == 16
    uf.merge(2, 3)
    uf.merge(0, 3)
    assert uf.component_value(2) == 28
    uf.rollback(value_state)
    assert uf.component_value(0) == 5
    assert uf.component_value(2) == 5
    assert uf.component_value(3) == 7
    uf.rollback(root_state)
    assert [uf.component_value(v) for v in range(4)] == [2, 3, 5, 7]


def test_random_rollback():
    rng = random.Random(0)
    for _ in range(1000):
        n = rng.randrange(1, 12)
        uf = RollbackUnionFind(n)
        operations = []
        for _ in range(100):
            if operations and rng.randrange(4) == 0:
                state = rng.randrange(len(operations) + 1)
                uf.rollback(state)
                del operations[state:]
            else:
                u = rng.randrange(n)
                v = rng.randrange(n)
                uf.merge(u, v)
                operations.append((u, v))

            parent = list(range(n))
            size = [1] * n

            def leader(x):
                while parent[x] != x:
                    x = parent[x]
                return x

            for u, v in operations:
                u = leader(u)
                v = leader(v)
                if u == v:
                    continue
                if size[u] < size[v]:
                    u, v = v, u
                parent[v] = u
                size[u] += size[v]
            assert uf.component_count == len({leader(v) for v in range(n)})
            for v in range(n):
                assert uf.size(v) == size[leader(v)]


if __name__ == "__main__":
    test_basic_rollback_and_snapshot()
    test_component_values()
    test_random_rollback()
