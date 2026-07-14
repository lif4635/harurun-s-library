import random
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[3]))

from library_codex.data_structure.StaticRMQ import StaticRMQ


def check_all(values):
    n = len(values)
    rmq = StaticRMQ(values)
    assert len(rmq) == n
    for l in range(n):
        best = l
        for r in range(l + 1, n + 1):
            if values[r - 1] < values[best]:
                best = r - 1
            assert rmq.argmin(l, r) == best
            assert rmq.query(l, r) == values[best]
            assert rmq.prod(l, r) == values[best]


def test_full_enumeration():
    assert len(StaticRMQ([])) == 0
    for n in range(1, 100):
        check_all([random.randrange(-10, 11) for _ in range(n)])
        check_all(list(range(n)))
        check_all(list(range(n, 0, -1)))


def test_random_large():
    for n in (127, 128, 129, 1000, 10000):
        values = [random.randrange(-10**30, 10**30) for _ in range(n)]
        rmq = StaticRMQ(values)
        for _ in range(20000):
            l = random.randrange(n)
            r = random.randrange(l + 1, n + 1)
            best = min(range(l, r), key=lambda i: (values[i], i))
            assert rmq.argmin(l, r) == best
            assert rmq.query(l, r) == values[best]


def test_million_without_recursion():
    n = 1000000
    values = [((i * 1000003) ^ (i << 17)) & ((1 << 60) - 1) for i in range(n)]
    rmq = StaticRMQ(values)
    for i in range(10000):
        l = i * 97 % n
        r = min(n, l + 1 + i * 193 % 1000)
        assert rmq.query(l, r) == min(values[l:r])


if __name__ == "__main__":
    random.seed(0)
    test_full_enumeration()
    test_random_large()
    test_million_without_recursion()
