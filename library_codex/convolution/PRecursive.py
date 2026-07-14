from library_codex.math.Matrix import linear_equation
from library_codex.math.PolynomialMatrix import polynomial_matrix_prefix_product
from library_codex.convolution.FormalPowerSeries import DEFAULT_MOD


def _evaluate(polynomial, point, mod):
    result = 0
    for coefficient in reversed(polynomial):
        result = (result * point + coefficient) % mod
    return result


def _multiply_linear(polynomial, constant, mod):
    result = [0] * (len(polynomial) + 1)
    for index, value in enumerate(polynomial):
        result[index] = (result[index] + value * constant) % mod
        result[index + 1] = (result[index + 1] + value) % mod
    return result


def find_p_recursive(sequence, coefficient_degree, mod=DEFAULT_MOD):
    n = len(sequence)
    degree = coefficient_degree
    if degree < 0:
        raise ValueError("coefficient_degree must be nonnegative")
    order = (n + 2) // (degree + 2) - 1
    if order <= 0:
        return []
    width = (order + 1) * (degree + 1)
    matrix = [[0] * width for _ in range(width - 1)]
    for row in range(width - 1):
        for shift in range(order + 1):
            power = 1
            value = sequence[row + shift] % mod
            offset = (degree + 1) * shift
            for exponent in range(degree + 1):
                matrix[row][offset + exponent] = value * power % mod
                power = power * (row + shift) % mod
    solution = linear_equation(matrix, [0] * (width - 1), mod)
    if solution is None or not solution[1]:
        return []
    coefficients = solution[1][0]
    result = []
    for shift in range(order + 1):
        polynomial = []
        constant = shift % mod
        offset = shift * (degree + 1)
        for exponent in range(degree, -1, -1):
            polynomial = _multiply_linear(polynomial, constant, mod) if polynomial else []
            if not polynomial:
                polynomial = [coefficients[offset + exponent] % mod]
            else:
                polynomial[0] = (polynomial[0]
                                 + coefficients[offset + exponent]) % mod
        while polynomial and polynomial[-1] == 0:
            polynomial.pop()
        result.append(polynomial)
    while result and not result[-1]:
        result.pop()
    result.reverse()
    return result


def enumerate_p_recursive(initial, recurrence, count, mod=DEFAULT_MOD):
    if count < 0:
        raise ValueError("count must be nonnegative")
    if count <= len(initial):
        return [value % mod for value in initial[:count]]
    if len(recurrence) < 2:
        raise ValueError("a positive-order recurrence is required")
    order = len(recurrence) - 1
    coefficients = list(reversed(recurrence))
    result = [value % mod for value in initial]
    result.extend([0] * (count - len(result)))
    for index in range(len(initial), count):
        point = index - order
        total = 0
        for shift in range(order):
            source = point + shift
            if source >= 0:
                total -= result[source] * _evaluate(
                    coefficients[shift], point, mod
                )
        denominator = _evaluate(coefficients[order], point, mod)
        result[index] = total % mod * pow(denominator, -1, mod) % mod
    return result


def kth_term_p_recursive(initial, recurrence, index, mod=DEFAULT_MOD):
    if index < 0:
        raise ValueError("index must be nonnegative")
    if index < len(initial):
        return initial[index] % mod
    order = len(recurrence) - 1
    if order <= 0 or len(initial) < order:
        raise ValueError("insufficient initial terms or invalid recurrence")
    matrix = [[[] for _ in range(order)] for _ in range(order)]
    for column in range(order):
        matrix[0][column] = [(-value) % mod for value in recurrence[column + 1]]
    for row in range(1, order):
        matrix[row][row - 1] = recurrence[0][:]
    denominator = [[recurrence[0][:]]]
    steps = index - order + 1
    product = polynomial_matrix_prefix_product(matrix, steps, mod)
    denominator_product = polynomial_matrix_prefix_product(
        denominator, steps, mod
    )[0][0]
    numerator = 0
    for column in range(order):
        numerator += product[0][column] * initial[order - 1 - column]
    return numerator % mod * pow(denominator_product, -1, mod) % mod


FindPRecursive = find_p_recursive
EnumPRecursive = enumerate_p_recursive
KthtermOfPRecursive = kth_term_p_recursive
