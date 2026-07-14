import bisect
import random
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[3]))

from library_codex.data_structure.WaveletMatrix import WaveletMatrix


def check(a):
    n = len(a)
    wm = WaveletMatrix(a)
    assert [wm[i] for i in range(n)] == a

    for _ in range(500):
        l = random.randrange(n + 1)
        r = random.randrange(l, n + 1)
        x = random.choice((
            -1,
            0,
            1,
            random.randrange(1 << 20),
            (1 << 60) + random.randrange(10),
        ))
        y = random.choice((0, 1, random.randrange(1 << 20), 1 << 61))
        lower, upper = sorted((x, y))
        part = sorted(a[l:r])

        assert wm.rank(l, r, x) == part.count(x)
        assert wm.count_lt(l, r, x) == bisect.bisect_left(part, x)
        assert wm.count_le(l, r, x) == bisect.bisect_right(part, x)
        assert wm.range_freq(l, r, x) == bisect.bisect_left(part, x)
        assert wm.range_freq(l, r, lower, upper) == (
            bisect.bisect_left(part, upper) - bisect.bisect_left(part, lower)
        )

        prev = part[bisect.bisect_left(part, x) - 1] if part and part[0] < x else -1
        nxt = part[bisect.bisect_left(part, x)] if bisect.bisect_left(part, x) < len(part) else -1
        le = part[bisect.bisect_right(part, x) - 1] if part and part[0] <= x else -1
        assert wm.prev_value(l, r, x) == prev
        assert wm.next_value(l, r, x) == nxt
        assert wm.max_le(l, r, x) == le
        assert wm.min_ge(l, r, x) == nxt

        if l < r:
            k = random.randrange(r - l)
            assert wm.kth_smallest(l, r, k) == part[k]
            assert wm.quantile(l, r, k) == part[k]
            assert wm.kth_largest(l, r, k) == part[-k - 1]


def test_boundaries_and_random():
    for n in (0, 1, 2, 63, 64, 65, 127, 128, 129):
        check([random.randrange(16) for _ in range(n)])
        check([0] * n)
    for _ in range(50):
        n = random.randrange(1, 100)
        a = [random.choice((0, random.randrange(1 << 20), random.randrange(1 << 60))) for _ in range(n)]
        check(a)


def test_full_enumeration():
    for n in range(1, 30):
        a = [random.randrange(8) for _ in range(n)]
        wm = WaveletMatrix(a)
        for l in range(n):
            for r in range(l + 1, n + 1):
                part = sorted(a[l:r])
                for k, x in enumerate(part):
                    assert wm.kth_smallest(l, r, k) == x
                for x in range(10):
                    assert wm.rank(l, r, x) == part.count(x)
                    assert wm.count_lt(l, r, x) == bisect.bisect_left(part, x)


if __name__ == "__main__":
    random.seed(0)
    test_boundaries_and_random()
    test_full_enumeration()
