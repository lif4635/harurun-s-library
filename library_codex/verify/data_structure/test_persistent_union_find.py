import random
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[3]))

from library_codex.data_structure.PersistentUnionFind import PersistentUnionFind


def naive_leader(data, x):
    while data[x] >= 0:
        x = data[x]
    return x


def test_random_branching():
    for n in range(1, 80):
        uf = PersistentUnionFind(n)
        versions = [[-1] * n]
        counts = [n]
        for _ in range(2000):
            base = random.randrange(len(versions))
            x = random.randrange(n)
            y = random.randrange(n)
            data = versions[base].copy()
            rx = naive_leader(data, x)
            ry = naive_leader(data, y)
            count = counts[base]
            if rx != ry:
                if data[rx] > data[ry]:
                    rx, ry = ry, rx
                data[rx] += data[ry]
                data[ry] = rx
                count -= 1
            version = uf.unite(x, y, base)
            versions.append(data)
            counts.append(count)
            assert version == len(versions) - 1
            assert uf.components(version) == count

            for _ in range(3):
                v = random.randrange(len(versions))
                x = random.randrange(n)
                y = random.randrange(n)
                rx = naive_leader(versions[v], x)
                ry = naive_leader(versions[v], y)
                assert uf.same(x, y, v) == (rx == ry)
                assert uf.leader(x, v) == rx
                assert uf.size(x, v) == -versions[v][rx]


def test_long_without_recursion():
    n = 100000
    uf = PersistentUnionFind(n)
    version = 0
    for i in range(20000):
        version = uf.unite(i, i + 1, version)
    assert uf.size(0, version) == 20001
    assert uf.size(0, 0) == 1
    assert uf.components(version) == n - 20000


if __name__ == "__main__":
    random.seed(0)
    test_random_branching()
    test_long_without_recursion()
