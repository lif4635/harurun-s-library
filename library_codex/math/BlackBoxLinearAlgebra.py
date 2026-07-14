import random

from library_codex.convolution.FormalPowerSeries import (
    DEFAULT_MOD,
    fps_divmod,
    fps_multiply,
)
from library_codex.convolution.LinearRecurrence import berlekamp_massey
from library_codex.math.Matrix import matrix_vector_multiply


class LinearOperator:
    __slots__ = ("n", "apply")

    def __init__(self, size, apply):
        self.n = size
        self.apply = apply

    def matvec(self, vector, mod=DEFAULT_MOD):
        return [value % mod for value in self.apply(vector)]


class SparseMatrix:
    __slots__ = ("n", "rows")

    def __init__(self, size):
        self.n = size
        self.rows = [[] for _ in range(size)]

    def add(self, row, column, value):
        self.rows[row].append((column, value))

    def matvec(self, vector, mod=DEFAULT_MOD):
        if len(vector) != self.n:
            raise ValueError("invalid vector size")
        result = [0] * self.n
        for row, entries in enumerate(self.rows):
            total = 0
            for column, value in entries:
                total += value * vector[column]
            result[row] = total % mod
        return result


def _size(operator):
    size = getattr(operator, "n", None)
    if size is None:
        size = len(operator)
    return size


def _apply(operator, vector, mod):
    method = getattr(operator, "matvec", None)
    if method is not None:
        return method(vector, mod)
    return matrix_vector_multiply(operator, vector, mod)


def _random_vector(size, mod, rng, nonzero=False):
    if nonzero:
        return [rng.randrange(1, mod) for _ in range(size)]
    return [rng.randrange(mod) for _ in range(size)]


def _vector_minimal_polynomial(operator, vector, mod, rng):
    size = _size(operator)
    projection = _random_vector(size, mod, rng)
    sequence = [0] * (size * 2 + 1)
    current = [value % mod for value in vector]
    for index in range(len(sequence)):
        total = 0
        for left, right in zip(projection, current):
            total += left * right
        sequence[index] = total % mod
        current = _apply(operator, current, mod)
    recurrence = berlekamp_massey(sequence, mod)
    return [-value % mod for value in reversed(recurrence)] + [1]


def black_box_minimal_polynomial(
    operator, mod=DEFAULT_MOD, vector=None, seed=None, trials=2
):
    size = _size(operator)
    if size == 0:
        return [1]
    if trials < 1:
        raise ValueError("trials must be positive")
    rng = random.Random(seed) if seed is not None else random
    if vector is None:
        vector = _random_vector(size, mod, rng)
    if len(vector) != size:
        raise ValueError("invalid vector size")
    result = [1]
    for _ in range(trials):
        candidate = _vector_minimal_polynomial(
            operator, vector, mod, rng
        )
        if len(candidate) > len(result):
            result = candidate
        if len(result) == size + 1:
            break
    return result


def _multiply_mod(first, second, polynomial, mod):
    product = fps_multiply(first, second, mod)
    if len(product) < len(polynomial):
        return product
    return fps_divmod(product, polynomial, mod)[1]


def _power_of_x(exponent, polynomial, mod):
    if exponent < 0:
        raise ValueError("exponent must be nonnegative")
    if len(polynomial) <= 1:
        return []
    result = [1]
    base = [0, 1]
    if len(polynomial) == 2:
        base = [-polynomial[0] % mod]
    while exponent:
        if exponent & 1:
            result = _multiply_mod(result, base, polynomial, mod)
        exponent >>= 1
        if exponent:
            base = _multiply_mod(base, base, polynomial, mod)
    return result


def black_box_power(
    operator, vector, exponent, mod=DEFAULT_MOD, seed=None, trials=3
):
    size = _size(operator)
    if len(vector) != size:
        raise ValueError("invalid vector size")
    polynomial = black_box_minimal_polynomial(
        operator, mod, vector, seed, trials
    )
    coefficients = _power_of_x(exponent, polynomial, mod)
    result = [0] * size
    current = [value % mod for value in vector]
    for coefficient in coefficients:
        if coefficient:
            for index in range(size):
                result[index] = (
                    result[index] + coefficient * current[index]
                ) % mod
        current = _apply(operator, current, mod)
    return result


def black_box_linear_solve(
    operator, vector, mod=DEFAULT_MOD, seed=None, trials=3
):
    size = _size(operator)
    if len(vector) != size:
        raise ValueError("invalid vector size")
    polynomial = black_box_minimal_polynomial(
        operator, mod, vector, seed, trials
    )
    if not polynomial or polynomial[0] == 0:
        return None
    result = [0] * size
    current = [value % mod for value in vector]
    for degree in range(1, len(polynomial)):
        coefficient = polynomial[degree]
        if coefficient:
            for index in range(size):
                result[index] = (
                    result[index] + coefficient * current[index]
                ) % mod
        current = _apply(operator, current, mod)
    scale = -pow(polynomial[0], -1, mod) % mod
    return [value * scale % mod for value in result]


def _scaled_operator(operator, scales, mod):
    size = _size(operator)

    def apply(vector):
        result = _apply(operator, vector, mod)
        return [result[index] * scales[index] % mod for index in range(size)]

    return LinearOperator(size, apply)


def black_box_determinant(
    operator, mod=DEFAULT_MOD, seed=None, trials=8
):
    size = _size(operator)
    if size == 0:
        return 1
    rng = random.Random(seed) if seed is not None else random
    for _ in range(trials):
        scales = _random_vector(size, mod, rng, True)
        scaled = _scaled_operator(operator, scales, mod)
        polynomial = black_box_minimal_polynomial(
            scaled, mod, seed=rng.randrange(1 << 63), trials=2
        )
        if polynomial[0] == 0:
            return 0
        if len(polynomial) != size + 1:
            continue
        product = 1
        for value in scales:
            product = product * value % mod
        determinant = polynomial[0] if size & 1 == 0 else -polynomial[0]
        return determinant * pow(product, -1, mod) % mod
    raise ArithmeticError("black-box determinant failed after all trials")


mat_minpoly = black_box_minimal_polynomial
fast_pow = black_box_power
fast_det = black_box_determinant
fast_linear_equation = black_box_linear_solve
ModMatrix = LinearOperator
