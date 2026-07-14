import random

from library_codex.convolution.FormalPowerSeries import (
    DEFAULT_MOD,
    fps_add,
    fps_multiply,
    fps_taylor_shift,
)
from library_codex.convolution.MultipointEvaluation import (
    polynomial_interpolation,
    sample_point_shift,
)
from library_codex.math.Matrix import (
    characteristic_polynomial,
    identity_matrix,
    inverse_matrix,
    matrix_determinant,
    matrix_multiply,
)


def _shape(matrix):
    size = len(matrix)
    for row in matrix:
        if len(row) != size:
            raise ValueError("polynomial matrix must be square")
    return size


def _evaluate(polynomial, point, mod):
    result = 0
    for coefficient in reversed(polynomial):
        result = (result * point + coefficient) % mod
    return result


def polynomial_matrix_determinant(matrix, mod=DEFAULT_MOD):
    size = _shape(matrix)
    if size == 0:
        return [1]
    degree = 0
    for row in matrix:
        maximum = 0
        for polynomial in row:
            maximum = max(maximum, len(polynomial) - 1)
        degree += maximum
    if degree >= mod:
        raise ValueError("determinant degree must be smaller than mod")
    points = list(range(degree + 1))
    values = [0] * (degree + 1)
    evaluated = [[0] * size for _ in range(size)]
    for point in points:
        for row in range(size):
            for column in range(size):
                evaluated[row][column] = _evaluate(
                    matrix[row][column], point, mod
                )
        values[point] = matrix_determinant(evaluated, mod)
    return polynomial_interpolation(points, values, mod)


def determinant_a_plus_xb(
    first, second, mod=DEFAULT_MOD, seed=None, trials=8
):
    size = len(first)
    if len(second) != size:
        raise ValueError("matrix shapes must be equal")
    for row, other in zip(first, second):
        if len(row) != size or len(other) != size:
            raise ValueError("matrices must be square and equally sized")
    if size == 0:
        return [1]
    rng = random.Random(seed) if seed is not None else random
    shifts = [0]
    shifts.extend(rng.randrange(mod) for _ in range(max(0, trials - 1)))
    for shift in shifts:
        shifted = [
            [
                (first[row][column] - shift * second[row][column]) % mod
                for column in range(size)
            ]
            for row in range(size)
        ]
        inverse = inverse_matrix(shifted, mod)
        if inverse is None:
            continue
        determinant = matrix_determinant(shifted, mod)
        transformed = matrix_multiply(second, inverse, mod)
        for row in range(size):
            for column in range(size):
                transformed[row][column] = -transformed[row][column] % mod
        polynomial = characteristic_polynomial(transformed, mod)
        polynomial.reverse()
        for index in range(size + 1):
            polynomial[index] = polynomial[index] * determinant % mod
        return fps_taylor_shift(polynomial, shift, mod)
    polynomial_matrix = [
        [
            [first[row][column] % mod, second[row][column] % mod]
            for column in range(size)
        ]
        for row in range(size)
    ]
    return polynomial_matrix_determinant(polynomial_matrix, mod)


def _shift_matrix_samples(samples, shift, mod):
    count = len(samples)
    size = len(samples[0])
    result = [[[0] * size for _ in range(size)] for _ in range(count)]
    for row in range(size):
        for column in range(size):
            values = [samples[index][row][column] for index in range(count)]
            shifted = sample_point_shift(values, shift, count, mod)
            for index in range(count):
                result[index][row][column] = shifted[index]
    return result


def polynomial_matrix_prefix_product(matrix, count, mod=DEFAULT_MOD):
    size = _shape(matrix)
    if count < 0:
        raise ValueError("count must be nonnegative")
    if size == 0:
        return []
    if count == 0:
        return identity_matrix(size)
    degree = 1
    for row in matrix:
        for polynomial in row:
            degree = max(degree, len(polynomial) - 1)
    rounded = 1
    while rounded < degree:
        rounded <<= 1
    degree = rounded
    block = 1
    while degree * block * block < count:
        block <<= 1
    if degree * block >= mod:
        raise ValueError("sample range must be smaller than mod")
    inverse_block = pow(block, -1, mod)
    samples = []
    for index in range(degree + 1):
        point = block * index % mod
        samples.append([
            [_evaluate(matrix[row][column], point, mod) for column in range(size)]
            for row in range(size)
        ])
    width = 1
    while width != block:
        fraction = width * inverse_block % mod
        first_shift = _shift_matrix_samples(samples, fraction, mod)
        second_shift = _shift_matrix_samples(
            samples, width * degree + 1, mod
        )
        third_shift = _shift_matrix_samples(
            samples, (width * degree + 1 + fraction) % mod, mod
        )
        boundary = width * degree + 1
        for index in range(boundary):
            samples[index] = matrix_multiply(
                first_shift[index], samples[index], mod
            )
            second_shift[index] = matrix_multiply(
                third_shift[index], second_shift[index], mod
            )
        samples.extend(second_shift[:-1])
        width <<= 1
    result = identity_matrix(size)
    index = 0
    while index + block <= count:
        result = matrix_multiply(samples[index // block], result, mod)
        index += block
    while index < count:
        point_matrix = [
            [_evaluate(matrix[row][column], index, mod) for column in range(size)]
            for row in range(size)
        ]
        result = matrix_multiply(point_matrix, result, mod)
        index += 1
    return result


def spanning_tree_polynomial(vertex_count, edges, mod=DEFAULT_MOD):
    if vertex_count <= 1:
        return [1]
    size = vertex_count - 1
    laplacian = [[[0] for _ in range(size)] for _ in range(size)]

    def add(row, column, polynomial, sign):
        value = [(sign * coefficient) % mod for coefficient in polynomial]
        laplacian[row][column] = fps_add(
            laplacian[row][column], value, mod
        )

    for edge in edges:
        if len(edge) == 2:
            first, second = edge
            weight = [1]
        else:
            first, second, weight = edge
            if isinstance(weight, int):
                weight = [weight]
        if first < size:
            add(first, first, weight, 1)
        if second < size:
            add(second, second, weight, 1)
        if first < size and second < size:
            add(first, second, weight, -1)
            add(second, first, weight, -1)
    return polynomial_matrix_determinant(laplacian, mod)


PolynomialMatrixDeterminant = polynomial_matrix_determinant
polynomial_matrix_prod = polynomial_matrix_prefix_product
detApBx = determinant_a_plus_xb
