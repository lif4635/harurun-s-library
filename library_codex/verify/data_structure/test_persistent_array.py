import random
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[3]))

from library_codex.data_structure.PersistentArray import PersistentArray


def test_random_branching():
    for shift in (1, 4, 5):
        for n in (1, 2, 15, 16, 17, 255, 256, 257):
            initial = [random.randrange(-100, 101) for _ in range(n)]
            array = PersistentArray(initial, shift=shift)
            versions = [initial]
            for _ in range(2000):
                base = random.randrange(len(versions))
                if random.randrange(4):
                    i = random.randrange(n)
                    x = random.randrange(-10**30, 10**30)
                    version = array.set(i, x, base)
                    nxt = versions[base].copy()
                    nxt[i] = x
                else:
                    version = array.fork(base)
                    nxt = versions[base]
                versions.append(nxt)
                assert version == len(versions) - 1
                for _ in range(3):
                    v = random.randrange(len(versions))
                    i = random.randrange(n)
                    assert array.get(i, v) == versions[v][i]
            assert array.tolist(-1) == versions[-1]


def test_huge_sparse_array_without_recursion():
    n = 10**30
    array = PersistentArray(n, default=-1)
    v1 = array.set(n - 1, 123)
    v2 = array.set(0, 456, v1)
    assert array.get(n - 1, 0) == -1
    assert array.get(n - 1, v1) == 123
    assert array.get(0, v2) == 456
    assert array.get(n // 2, v2) == -1


if __name__ == "__main__":
    random.seed(0)
    test_random_branching()
    test_huge_sparse_array_without_recursion()
