import random

import pytest

from library_codex.linear_algebra.F2Matrix import F2Matrix


def test_product_power_inverse_and_semiring():
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


def test_dense_block_product_and_sparse_rectangles():
    rng = random.Random(184736)
    for height, middle, width in ((400, 73, 137), (300, 64, 97), (3, 4097, 19), (0, 8, 3), (9, 0, 7), (7, 5, 0)):
        for dense in (False, True):
            left = [rng.getrandbits(middle) if dense else (1 << rng.randrange(middle) if middle else 0)
                    for _ in range(height)]
            right = [rng.getrandbits(width) for _ in range(middle)]
            a = F2Matrix(height, middle, left)
            b = F2Matrix(middle, width, right)
            expected = []
            for bits in left:
                value = 0
                for column, row in enumerate(right):
                    if bits >> column & 1:
                        value ^= row
                expected.append(value)
            assert a.multiply(b).rows == expected
            assert a.rows == left and b.rows == right
    with pytest.raises(ValueError):
        F2Matrix(2, 3).multiply(F2Matrix(2, 2))


def test_rank_matches_sweep_and_preserves_rows():
    rng = random.Random(192847)
    for height in range(25):
        for width in (0, 1, 7, 24, 31, 257):
            for _ in range(10):
                rows = [rng.getrandbits(width) for _ in range(height)]
                matrix = F2Matrix(height, width, rows)
                assert matrix.rank() == matrix.copy().sweep()[0]
                assert matrix.rows == rows
    matrix = F2Matrix(4, 1000000, [1 << 999999, 1, (1 << 999999) | 1, 0])
    assert matrix.rank() == 2
    assert F2Matrix(200, 200, [0] * 200).rank() == 0


def test_inverse_pivots_and_singular_boundaries():
    for size in (0, 1, 8, 33, 129):
        matrix = F2Matrix(size, size, [1 << (size - i - 1) for i in range(size)])
        assert matrix.inverse() == matrix
    assert F2Matrix(3, 3, [1, 1, 4]).inverse() is None
    with pytest.raises(ValueError):
        F2Matrix(2, 3).inverse()


def test_block_inverse_matches_scalar_elimination():
    rng = random.Random(846192)
    for size in (127, 128, 129, 191, 255):
        for _ in range(8):
            source = [rng.getrandbits(size) for _ in range(size)]
            matrix = F2Matrix(size, size, source)
            augmented = F2Matrix(size, 2 * size, [row | 1 << (size + i) for i, row in enumerate(source)])
            rank, _ = augmented.sweep(size)
            result = matrix.inverse()
            if rank < size:
                assert result is None
            else:
                assert result.rows == [row >> size for row in augmented.rows]
                assert matrix.multiply(result) == F2Matrix.identity(size)
            assert matrix.rows == source
    for size in (128, 129, 256):
        rows = [1 << i for i in range(size)]
        for duplicate in (0, 7, 8, 127):
            copy = rows.copy()
            copy[duplicate] = rows[(duplicate + 1) % size]
            assert F2Matrix(size, size, copy).inverse() is None


def test_solve_matches_all_small_solutions():
    rng = random.Random(717389)
    for height in range(8):
        for width in range(8):
            for _ in range(30):
                rows = [rng.getrandbits(width) for _ in range(height)]
                matrix = F2Matrix(height, width, rows)
                rhs = rng.getrandbits(height)
                expected = {value for value in range(1 << width)
                            if matrix.matvec(value) == rhs}
                answer = matrix.solve(rhs)
                assert answer == matrix.solve([(rhs >> i) & 1 for i in range(height)])
                assert matrix.rows == rows
                if not expected:
                    assert answer is None
                    continue
                particular, kernel = answer
                generated = {particular}
                for value in kernel:
                    assert matrix.matvec(value) == 0
                    generated |= {previous ^ value for previous in tuple(generated)}
                assert len(generated) == 1 << len(kernel)
                assert generated == expected
    for rhs in (-1, 4, [], [0, 1, 0]):
        with pytest.raises(ValueError):
            F2Matrix(2, 3).solve(rhs)


def test_sweep_and_solve_rectangular_block_boundaries():
    rng = random.Random(861921)
    for height, width in ((127, 129), (128, 128), (129, 257), (257, 129), (256, 256)):
        for rank_limit in (0, 1, 7, 8, 9, min(height, width)):
            generators = [rng.getrandbits(width) for _ in range(rank_limit)]
            source = []
            for i in range(height):
                row = 0
                for value in generators:
                    if rng.randrange(2):
                        row ^= value
                source.append(row)
            matrix = F2Matrix(height, width, source)
            rhs = matrix.matvec(rng.getrandbits(width))
            augmented = [row | ((rhs >> i) & 1) << width for i, row in enumerate(source)]
            expected = augmented.copy()
            pivots = []
            for column in range(width):
                found = next((i for i in range(len(pivots), height)
                              if expected[i] >> column & 1), None)
                if found is None:
                    continue
                pivot = len(pivots)
                expected[pivot], expected[found] = expected[found], expected[pivot]
                for i in range(height):
                    if i != pivot and expected[i] >> column & 1:
                        expected[i] ^= expected[pivot]
                pivots.append(column)
            combined = F2Matrix(height, width + 1, augmented)
            assert combined.sweep(width) == (len(pivots), pivots)
            assert combined.rows == expected
            particular, kernel = matrix.solve(rhs)
            assert matrix.matvec(particular) == rhs
            assert len(kernel) == width - len(pivots)
            assert F2Matrix(len(kernel), width, kernel).rank() == len(kernel)
            assert all(matrix.matvec(value) == 0 for value in kernel)
            assert matrix.rows == source
    with pytest.raises(ValueError):
        F2Matrix(2, 3).sweep(4)
