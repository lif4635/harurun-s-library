import math
import random
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT.parent))

from library_codex.algorithm.IntegerUtilities import integer_nth_root  # noqa: E402
from library_codex.math.BinomialQueries import BinomialPrefix  # noqa: E402
from library_codex.math.Combination import Combination  # noqa: E402
from library_codex.math.GrayCode import gray_code_path  # noqa: E402


def test_integer_nth_root_exact_boundaries():
    rng = random.Random(411)
    for degree in range(1, 65):
        for _ in range(100):
            number = rng.getrandbits(256)
            root = integer_nth_root(number, degree)
            assert root ** degree <= number < (root + 1) ** degree
        base = rng.randrange(2, 10**6)
        power = base ** degree
        assert integer_nth_root(power, degree) == base
        assert integer_nth_root(power - 1, degree) == base - 1


def test_gray_code_hamilton_paths():
    for bit_count in range(1, 8):
        limit = 1 << bit_count
        rng = random.Random(bit_count)
        for _ in range(100):
            start = rng.randrange(limit)
            goal = rng.randrange(limit)
            if (start ^ goal).bit_count() & 1 == 0:
                goal ^= 1
            path = list(gray_code_path(bit_count, start, goal))
            assert path[0] == start and path[-1] == goal
            assert len(path) == limit and len(set(path)) == limit
            assert all((first ^ second).bit_count() == 1
                       for first, second in zip(path, path[1:]))


def test_binomial_prefix_moves_arbitrarily():
    mod = 998244353
    combination = Combination(200, mod)
    prefix = BinomialPrefix(combination)
    rng = random.Random(412)
    for _ in range(2_000):
        n = rng.randrange(201)
        m = rng.randrange(n + 1)
        expected = sum(math.comb(n, k) for k in range(m + 1)) % mod
        assert prefix.move(n, m) == expected
        assert prefix.get() == expected
