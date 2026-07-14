import random
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[3]))

from library_codex.data_structure.PersistentSegmentTree import PersistentSegmentTree


def test_random_branching_sum():
    for n in (0, 1, 2, 31, 32, 33, 100):
        initial = [random.randrange(-100, 101) for _ in range(n)]
        seg = PersistentSegmentTree(initial, lambda x, y: x + y, 0)
        versions = [initial]
        for _ in range(3000):
            base = random.randrange(len(versions))
            cmd = random.randrange(3) if n else 2
            if cmd == 0:
                i = random.randrange(n)
                x = random.randrange(-100, 101)
                version = seg.set(i, x, base)
                nxt = versions[base].copy()
                nxt[i] = x
                versions.append(nxt)
            elif cmd == 1:
                i = random.randrange(n)
                x = random.randrange(-100, 101)
                version = seg.add(i, x, base)
                nxt = versions[base].copy()
                nxt[i] = x + nxt[i]
                versions.append(nxt)
            else:
                version = seg.fork(base)
                versions.append(versions[base])
            assert version == len(versions) - 1

            for _ in range(3):
                v = random.randrange(len(versions))
                l = random.randrange(n + 1)
                r = random.randrange(l, n + 1)
                assert seg.prod(l, r, v) == sum(versions[v][l:r])
                if n:
                    i = random.randrange(n)
                    assert seg.get(i, v) == versions[v][i]
                assert seg.all_prod(v) == sum(versions[v])


def test_non_commutative_order():
    a = list("persistent")
    seg = PersistentSegmentTree(a, lambda x, y: x + y, "")
    assert seg.prod(0, len(a)) == "persistent"
    v1 = seg.set(0, "P")
    assert seg.prod(0, len(a), v1) == "Persistent"
    assert seg.prod(0, len(a), 0) == "persistent"
    v2 = seg.add(1, "!", v1)
    assert seg.get(1, v2) == "!e"
    assert seg.prod(0, 3, v2) == "P!er"


def test_large_without_recursion():
    n = 100000
    seg = PersistentSegmentTree(n, lambda x, y: x + y, 0)
    version = 0
    expected = 0
    for i in range(50000):
        value = i + 1
        version = seg.set(i * 2, value, version)
        expected += value
    assert seg.all_prod(version) == expected
    assert seg.prod(0, n, 0) == 0
    assert seg.prod(0, n, version) == expected


if __name__ == "__main__":
    random.seed(0)
    test_random_branching_sum()
    test_non_commutative_order()
    test_large_without_recursion()
