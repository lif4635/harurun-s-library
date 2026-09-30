from math import prod
import importlib
import random

from library_codex.benchmarks.bivariate_candidates import colored_inverse, row_inverse, sparse_unlimited
from library_codex.benchmarks.compare_bivariate_methods import coefficients
from library_codex.benchmarks.profile_bivariate import profile
from library_codex.fps.MultivariateFPS import MultivariateFormalPowerSeries


def inverse_naive(values, width):
    mod = 998244353
    result = [pow(values[0], -1, mod)] + [0] * (len(values) - 1)
    for i in range(1, len(values)):
        result[i] = -result[0] * sum(values[j] * result[i-j] for j in range(1, i+1) if j % width <= i % width) % mod
    return result


def test_inverse_candidates_and_prefixes():
    rng = random.Random(53248)
    for base in ((1, 1), (1, 23), (23, 1), (3, 11), (11, 3), (8, 8), (17, 19)):
        size = prod(base)
        for _ in range(4):
            values = [rng.randrange(998244353) for _ in range(size)]
            values[0] = 7
            expected = inverse_naive(values, base[0])
            for candidate in (colored_inverse, row_inverse):
                for prefix in sorted({1, size, max(1, size // 2), min(size, base[0]+1)}):
                    assert candidate(values, base, 998244353, prefix) == expected[:prefix]
                    short = values[:max(1, prefix // 2)]
                    wanted = inverse_naive(short + [0] * (prefix - len(short)), base[0])
                    assert candidate(short, base, 998244353, prefix) == wanted


def test_sparse_candidates_and_input_families():
    mod = 998244353
    for family in ("sparse-low", "sparse-random"):
        for base in ((1, 33), (33, 1), (5, 7), (7, 5)):
            for count in (0, 8, 16, 17, 32):
                for operation in ("inverse", "logarithm", "exponential", "power"):
                    values = coefficients(*base, operation, family, count, 8427)
                    assert sum(value != 0 for value in values[1:]) == min(count, prod(base)-1)
                    source = MultivariateFormalPowerSeries(values, base)
                    exponent = -5 if operation == "power" else -1 if operation == "inverse" else None
                    got = sparse_unlimited(values, base, mod, exponent, operation == "logarithm")
                    expected = source.power(-5).coefficients if operation == "power" else getattr(source, operation)().coefficients
                    assert got == expected


def test_transform_profile_restores_functions():
    module = importlib.import_module("library_codex.fps.MultivariateFPS")
    ntt = importlib.import_module("library_codex.convolution.NTT998")
    multiplication = importlib.import_module("library_codex.convolution.MultivariateMultiplication")
    fps = importlib.import_module("library_codex.fps998.FPS")
    before = (module._inverse_prefix, module._sparse_2d,
              ntt._butterfly, ntt._butterfly_inv, fps._butterfly, multiplication._multiply998)
    for mode in ("current", "colored", "row"):
        result = profile(17, 19, "inverse", mode)
        assert result["calls"] > 0
        assert result["calls"] == sum(row["count"] for row in result["transforms"])
        assert result["lengthLog2Length"] > 0
        assert before == (module._inverse_prefix, module._sparse_2d,
                          ntt._butterfly, ntt._butterfly_inv, fps._butterfly, multiplication._multiply998)
