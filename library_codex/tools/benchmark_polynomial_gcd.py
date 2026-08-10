"""Compare Half-GCD polynomial operations with the Euclidean baseline."""

import argparse
import random
import sys
import time
from pathlib import Path


sys.path.append(str(Path(__file__).resolve().parents[2]))

from library_codex.polynomial.PolynomialDivision import poly_divmod, poly_mod
from library_codex.polynomial.PolynomialGCD import polynomial_gcd
from library_codex.polynomial.PolynomialResultant import polynomial_resultant


MOD = 998244353


def naive_gcd(first, second):
    while second:
        first, second = second, poly_mod(first, second)
    if not first:
        return []
    inverse = pow(first[-1], MOD - 2, MOD)
    return [value * inverse % MOD for value in first]


def naive_resultant(first, second):
    result = 1
    sign = 0
    while True:
        _, remainder = poly_divmod(first, second)
        first_degree = len(first) - 1
        second_degree = len(second) - 1
        if not remainder:
            if second_degree:
                return 0
            result = result * pow(second[0], first_degree, MOD) % MOD
            return -result % MOD if sign else result
        remainder_degree = len(remainder) - 1
        sign ^= first_degree & second_degree & 1
        result = result * pow(
            second[-1], first_degree - remainder_degree, MOD
        ) % MOD
        first, second = second, remainder


def measure(function, *arguments):
    started = time.perf_counter()
    result = function(*arguments)
    return time.perf_counter() - started, result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--degree", type=int, default=4096)
    args = parser.parse_args()
    rng = random.Random(981723)
    first = [rng.randrange(MOD) for _ in range(args.degree + 1)]
    second = [rng.randrange(MOD) for _ in range(args.degree)]

    fast_gcd_time, fast_gcd = measure(polynomial_gcd, first, second)
    naive_gcd_time, expected_gcd = measure(naive_gcd, first, second)
    fast_resultant_time, fast_resultant = measure(
        polynomial_resultant, first, second
    )
    naive_resultant_time, expected_resultant = measure(
        naive_resultant, first, second
    )
    if fast_gcd != expected_gcd or fast_resultant != expected_resultant:
        raise AssertionError("Half-GCD result mismatch")
    fast = fast_gcd_time + fast_resultant_time
    naive = naive_gcd_time + naive_resultant_time
    checksum = (sum(fast_gcd) + fast_resultant) % MOD
    print(f"degree={args.degree}")
    print(f"euclid={naive:.6f}s")
    print(f"half_gcd={fast:.6f}s")
    print(f"ratio={naive / fast:.3f}x")
    print(f"total={fast:.6f}s")
    print(f"checksum={checksum}")


if __name__ == "__main__":
    main()
