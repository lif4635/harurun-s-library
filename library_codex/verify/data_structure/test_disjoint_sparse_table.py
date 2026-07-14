import random
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[3]))

from library_codex.data_structure.DisjointSparseTable import DisjointSparseTable


def test_min():
    for n in range(1, 80):
        a = [random.randrange(-100, 101) for _ in range(n)]
        dst = DisjointSparseTable(min, a)
        for l in range(n):
            ans = a[l]
            for r in range(l + 1, n + 1):
                if r != l + 1:
                    ans = min(ans, a[r - 1])
                assert dst.prod(l, r) == ans


def test_non_commutative():
    # Affine functions x -> ax+b. The product applies functions left-to-right.
    mod = 998244353

    def op(f, g):
        a, b = f
        c, d = g
        return a * c % mod, (b * c + d) % mod

    for n in range(1, 60):
        a = [(random.randrange(mod), random.randrange(mod)) for _ in range(n)]
        dst = DisjointSparseTable(op, a)
        for _ in range(200):
            l = random.randrange(n)
            r = random.randrange(l + 1, n + 1)
            ans = a[l]
            for x in a[l + 1:r]:
                ans = op(ans, x)
            assert dst.query(l, r) == ans


def test_empty_build():
    dst = DisjointSparseTable(min, [])
    assert dst.n == 0


if __name__ == "__main__":
    random.seed(0)
    test_min()
    test_non_commutative()
    test_empty_build()
