import random

import pytest

from library_codex.fps.SparseFormalPowerSeries import sparse_differential, sparse_exponential, sparse_power


def test_random_differential_identity():
    rng = random.Random(883)
    for mod in (17, 101, 998244353):
        for n in range(1, min(mod, 40)):
            for _ in range(15):
                a = [rng.randrange(mod) if rng.randrange(3) == 0 else 0 for _ in range(rng.randrange(12))]
                b = [rng.randrange(1, mod)] + [rng.randrange(mod) if rng.randrange(3) == 0 else 0 for _ in range(rng.randrange(12))]
                constant = rng.randrange(mod)
                f = sparse_differential(a, b, n, constant, mod)
                assert len(f) == n and f[0] == constant
                for k in range(n - 1):
                    left = sum(b[j] * (k - j + 1) * f[k - j + 1] for j in range(min(k + 1, len(b))))
                    right = sum(a[j] * f[k - j] for j in range(min(k + 1, len(a))))
                    assert (left - right) % mod == 0


def test_exp_power_and_validation():
    f = [0, 2, 0, 0, 7]
    derivative = [i * f[i] for i in range(1, len(f))]
    assert sparse_differential(derivative, [1], 100) == sparse_exponential(f, 100)
    f = [1, 2, 0, 3]
    assert sparse_differential([5 * i * f[i] for i in range(1, len(f))], f, 100) == sparse_power(f, 5, 100)
    assert sparse_differential([], [1], 1, 8) == [8]
    assert sparse_differential([], [1], 0) == []
    with pytest.raises(ValueError):
        sparse_differential([], [1], -1)
    with pytest.raises(ValueError):
        sparse_differential([], [1], 18, mod=17)
    with pytest.raises(ZeroDivisionError):
        sparse_differential([], [0], 10)
