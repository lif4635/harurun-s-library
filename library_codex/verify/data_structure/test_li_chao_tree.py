import random
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[3]))

from library_codex.data_structure.LiChaoTree import (
    INF,
    DynamicLiChaoTree,
    LiChaoTree,
)


def test_fixed_random():
    for n in (1, 2, 3, 31, 32, 33, 63, 64, 65):
        xs = sorted(random.sample(range(-1000, 1001), n))
        for minimize in (True, False):
            tree = LiChaoTree(xs + xs[:n // 3], minimize)
            lines = []
            empty = INF if minimize else -INF
            assert all(tree.query(x) == empty for x in xs)
            for _ in range(2000):
                if random.randrange(3):
                    a = random.randrange(-10**6, 10**6)
                    b = random.randrange(-10**12, 10**12)
                    if random.randrange(2):
                        tree.add_line(a, b)
                        lines.append((a, b, xs[0], xs[-1] + 1))
                    else:
                        l = random.randrange(n + 1)
                        r = random.randrange(l, n + 1)
                        tree.add_segment_index(a, b, l, r)
                        if l < r:
                            lines.append((a, b, xs[l], xs[r - 1] + 1))
                else:
                    i = random.randrange(n)
                    x = xs[i]
                    values = [a * x + b for a, b, l, r in lines if l <= x < r]
                    want = (min(values) if minimize else max(values)) if values else empty
                    assert tree.query(x) == want
                    assert tree.query_index(i) == want


def test_fixed_value_segments():
    xs = [-10, -3, 0, 7, 20]
    tree = LiChaoTree(xs)
    tree.add_segment(2, 5, -4, 20)
    assert tree.query(-10) == INF
    assert tree.query(-3) == -1
    assert tree.query(0) == 5
    assert tree.query(7) == 19
    assert tree.query(20) == INF


def test_dynamic_random():
    low, high = -40, 41
    for minimize in (True, False):
        tree = DynamicLiChaoTree(low, high, minimize)
        lines = []
        empty = INF if minimize else -INF
        for _ in range(5000):
            if random.randrange(3):
                a = random.randrange(-1000, 1001)
                b = random.randrange(-10000, 10001)
                if random.randrange(2):
                    tree.add_line(a, b)
                    lines.append((a, b, low, high))
                else:
                    l = random.randrange(low, high + 1)
                    r = random.randrange(l, high + 1)
                    tree.add_segment(a, b, l, r)
                    if l < r:
                        lines.append((a, b, l, r))
            else:
                x = random.randrange(low, high)
                values = [a * x + b for a, b, l, r in lines if l <= x < r]
                want = (min(values) if minimize else max(values)) if values else empty
                assert tree.query(x) == want


def test_huge_domain_without_recursion():
    low = -10**30
    high = 10**30 + 1
    tree = DynamicLiChaoTree(low, high)
    lines = []
    for _ in range(1000):
        a = random.randrange(-10**18, 10**18)
        b = random.randrange(-10**30, 10**30)
        if random.randrange(2):
            tree.add_line(a, b)
            lines.append((a, b, low, high))
        else:
            l = random.randrange(low, high)
            r = random.randrange(l, high + 1)
            tree.add_segment(a, b, l, r)
            lines.append((a, b, l, r))
    for _ in range(1000):
        x = random.randrange(low, high)
        values = [a * x + b for a, b, l, r in lines if l <= x < r]
        want = min(values) if values else INF
        assert tree.query(x) == want


if __name__ == "__main__":
    random.seed(0)
    test_fixed_random()
    test_fixed_value_segments()
    test_dynamic_random()
    test_huge_domain_without_recursion()
