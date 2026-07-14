import random
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[3]))

from library_codex.data_structure.SegmentTreeBeats import INF, SegmentTreeBeats


def check_random(a, q):
    n = len(a)
    seg = SegmentTreeBeats(a)
    for _ in range(q):
        l = random.randrange(n + 1)
        r = random.randrange(l, n + 1)
        cmd = random.randrange(10)
        if cmd == 0:
            x = random.randrange(-100, 101)
            seg.range_chmin(l, r, x)
            a[l:r] = [min(v, x) for v in a[l:r]]
        elif cmd == 1:
            x = random.randrange(-100, 101)
            seg.range_chmax(l, r, x)
            a[l:r] = [max(v, x) for v in a[l:r]]
        elif cmd == 2:
            x = random.randrange(-100, 101)
            seg.range_add(l, r, x)
            a[l:r] = [v + x for v in a[l:r]]
        elif cmd == 3:
            x = random.randrange(-100, 101)
            seg.range_update(l, r, x)
            a[l:r] = [x] * (r - l)
        elif cmd == 4:
            assert seg.range_sum(l, r) == sum(a[l:r])
        elif cmd == 5:
            want = min(a[l:r]) if l < r else INF
            assert seg.range_min(l, r) == want
        elif cmd == 6:
            want = max(a[l:r]) if l < r else -INF
            assert seg.range_max(l, r) == want
        elif cmd == 7 and n:
            p = random.randrange(n)
            x = random.randrange(-100, 101)
            seg.set(p, x)
            a[p] = x
        elif cmd == 8 and n:
            p = random.randrange(n)
            assert seg.get(p) == a[p]
        else:
            assert seg.all_sum() == sum(a)
            assert seg.all_min() == (min(a) if a else INF)
            assert seg.all_max() == (max(a) if a else -INF)

        if random.randrange(20) == 0:
            assert [seg.get(i) for i in range(n)] == a
            assert seg.all_sum() == sum(a)


def test_random():
    for n in (0, 1, 2, 3, 31, 32, 33, 63, 64, 65):
        check_random([random.randrange(-100, 101) for _ in range(n)], 3000)
    for _ in range(100):
        n = random.randrange(1, 100)
        check_random([random.randrange(-100, 101) for _ in range(n)], 1000)


def test_large_integers():
    big = 10**60
    a = [-big, big, 0, big - 1, -big + 1]
    seg = SegmentTreeBeats(a)
    seg.range_chmin(0, 5, big // 2)
    a = [min(x, big // 2) for x in a]
    seg.range_chmax(1, 5, -big // 2)
    a[1:5] = [max(x, -big // 2) for x in a[1:5]]
    seg.range_add(0, 4, big * 3)
    a[:4] = [x + big * 3 for x in a[:4]]
    assert seg.range_sum(0, 5) == sum(a)
    assert seg.range_min(0, 5) == min(a)
    assert seg.range_max(0, 5) == max(a)


def test_long_without_recursion():
    n = 100000
    a = [i & 1023 for i in range(n)]
    seg = SegmentTreeBeats(a)
    seg.range_chmin(0, n, 700)
    seg.range_chmax(1, n - 1, 300)
    seg.range_add(100, n - 100, 17)
    seg.range_update(1000, n - 1000, 42)
    a = [min(x, 700) for x in a]
    a[1:n - 1] = [max(x, 300) for x in a[1:n - 1]]
    a[100:n - 100] = [x + 17 for x in a[100:n - 100]]
    a[1000:n - 1000] = [42] * (n - 2000)
    assert seg.range_sum(0, n) == sum(a)
    assert seg.range_min(0, n) == min(a)
    assert seg.range_max(0, n) == max(a)
    assert seg.get(0) == a[0]
    assert seg.get(n - 1) == a[-1]


if __name__ == "__main__":
    random.seed(0)
    test_random()
    test_large_integers()
    test_long_without_recursion()
