from itertools import permutations
import random

from library_codex.math.AdvancedMatrix import (
    determinant_arbitrary_mod,
    directed_spanning_tree_count,
    hafnian,
    pfaffian,
    spanning_tree_count,
)
from library_codex.math.F2Matrix import F2Matrix
from library_codex.math.Matrix import matrix_determinant


MOD = 998244353


def brute_determinant(matrix, mod):
    result = 0
    for order in permutations(range(len(matrix))):
        product = 1
        inversions = 0
        for row, column in enumerate(order):
            product *= matrix[row][column]
            for earlier in range(row):
                inversions += order[earlier] > column
        result += -product if inversions & 1 else product
    return result % mod


def brute_hafnian(matrix, mod):
    size = len(matrix)
    dp = [0] * (1 << size)
    dp[0] = 1
    for mask in range(1, 1 << size):
        if mask.bit_count() & 1:
            continue
        first_bit = mask & -mask
        first = first_bit.bit_length() - 1
        remaining = mask ^ first_bit
        bits = remaining
        while bits:
            bit = bits & -bits
            second = bit.bit_length() - 1
            dp[mask] += matrix[first][second] * dp[remaining ^ bit]
            bits ^= bit
        dp[mask] %= mod
    return dp[-1]


def test_arbitrary_mod_determinant_against_permutations():
    rng = random.Random(18374)
    moduli = [1, 2, 4, 6, 8, 9, 12, 36, 1000, 998244352]
    for size in range(7):
        for _ in range(250):
            matrix = [
                [rng.randrange(-1000, 1001) for _ in range(size)]
                for _ in range(size)
            ]
            for mod in moduli:
                assert determinant_arbitrary_mod(matrix, mod) == brute_determinant(
                    matrix, mod
                )


def test_f2_matrix_product_power_inverse_and_semiring():
    rng = random.Random(918374)
    for size in range(25):
        for _ in range(100):
            first = F2Matrix(size, size, [rng.getrandbits(size) for _ in range(size)])
            second = F2Matrix(size, size, [rng.getrandbits(size) for _ in range(size)])
            product = first * second
            or_product = first.and_or_product(second)
            for row in range(size):
                for column in range(size):
                    expected = 0
                    expected_or = 0
                    for pivot in range(size):
                        value = first.get(row, pivot) & second.get(pivot, column)
                        expected ^= value
                        expected_or |= value
                    assert product.get(row, column) == expected
                    assert or_product.get(row, column) == expected_or
            inverse = first.inverse()
            if first.determinant():
                assert first * inverse == F2Matrix.identity(size)
            else:
                assert inverse is None
        identity = F2Matrix.identity(size)
        assert identity.power(10**18) == identity


def test_hafnian_and_pfaffian_random_small():
    rng = random.Random(718293)
    for size in range(0, 14, 2):
        for _ in range(300):
            symmetric = [[0] * size for _ in range(size)]
            skew = [[0] * size for _ in range(size)]
            for row in range(size):
                for column in range(row):
                    value = rng.randrange(MOD)
                    symmetric[row][column] = value
                    symmetric[column][row] = value
                    value = rng.randrange(MOD)
                    skew[row][column] = value
                    skew[column][row] = -value % MOD
            assert hafnian(symmetric, MOD) == brute_hafnian(symmetric, MOD)
            determinant = matrix_determinant(skew, MOD)
            value = pfaffian(skew, MOD)
            assert value * value % MOD == determinant


def test_matrix_tree_complete_and_directed_brutish_cases():
    for size in range(1, 30):
        edges = [(first, second) for first in range(size) for second in range(first)]
        assert spanning_tree_count(size, edges, MOD) == pow(size, size - 2, MOD)
    inward = [(0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1)]
    assert directed_spanning_tree_count(3, inward, 0, True, MOD) == 3
    assert directed_spanning_tree_count(3, inward, 0, False, MOD) == 3
    assert directed_spanning_tree_count(
        4, [(1, 0), (2, 1), (3, 1)], 0, True, MOD
    ) == 1
