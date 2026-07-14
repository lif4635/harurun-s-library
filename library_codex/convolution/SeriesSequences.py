from library_codex.convolution.FormalPowerSeries import (
    DEFAULT_MOD,
    fps_exponential,
    fps_inverse,
    fps_logarithm,
    fps_multiply,
    fps_power,
    fps_shrink,
    fps_taylor_shift,
)
from library_codex.convolution.PolynomialComposition import fps_compose
from library_codex.math.ModularArithmetic import modular_square_root


def _factorials(size, mod):
    if size >= mod:
        raise ValueError("series degree must be smaller than mod")
    factorial = [1] * (size + 1)
    for index in range(1, size + 1):
        factorial[index] = factorial[index - 1] * index % mod
    inverse_factorial = [1] * (size + 1)
    if size:
        inverse_factorial[-1] = pow(factorial[-1], -1, mod)
        for index in range(size, 0, -1):
            inverse_factorial[index - 1] = (
                inverse_factorial[index] * index % mod
            )
    return factorial, inverse_factorial


def stirling_first_row(order, mod=DEFAULT_MOD, signed=False):
    """Coefficients of rising factorial x(x+1)...(x+order-1)."""
    if order < 0:
        raise ValueError("order must be nonnegative")
    if order == 0:
        return [1]
    polynomial = [0, 1]
    for bit in range(order.bit_length() - 2, -1, -1):
        current = order >> bit
        shifted = fps_taylor_shift(polynomial, current >> 1, mod)
        polynomial = fps_multiply(polynomial, shifted, mod)
        if current & 1:
            result = [0] * (len(polynomial) + 1)
            scale = current - 1
            for index, value in enumerate(polynomial):
                result[index] = (result[index] + value * scale) % mod
                result[index + 1] = (result[index + 1] + value) % mod
            polynomial = result
    if signed:
        for index in range(order + 1):
            if (order - index) & 1:
                polynomial[index] = -polynomial[index] % mod
    return polynomial


def stirling_second_row(order, mod=DEFAULT_MOD):
    """Return S(order, 0), ..., S(order, order)."""
    if order < 0:
        raise ValueError("order must be nonnegative")
    factorial, inverse_factorial = _factorials(order, mod)
    powers = [pow(index, order, mod) * inverse_factorial[index] % mod
              for index in range(order + 1)]
    signs = [(-inverse_factorial[index] if index & 1 else inverse_factorial[index]) % mod
             for index in range(order + 1)]
    return fps_multiply(powers, signs, mod)[:order + 1]


def stirling_first_column(column, upper, mod=DEFAULT_MOD):
    """Unsigned first-kind Stirling numbers s(n, column), column <= n <= upper."""
    if column < 0 or upper < 0:
        raise ValueError("indices must be nonnegative")
    if upper < column:
        return []
    factorial, inverse_factorial = _factorials(upper, mod)
    logarithm = [0] + [pow(index, -1, mod) for index in range(1, upper + 1)]
    values = fps_power(logarithm, column, upper + 1, mod)
    scale = inverse_factorial[column]
    result = [0] * (upper + 1)
    for index in range(column, upper + 1):
        result[index] = values[index] * scale % mod * factorial[index] % mod
    return result


def stirling_second_column(column, upper, mod=DEFAULT_MOD):
    """Second-kind Stirling numbers S(n, column), column <= n <= upper."""
    if column < 0 or upper < 0:
        raise ValueError("indices must be nonnegative")
    if upper < column:
        return []
    factorial, inverse_factorial = _factorials(upper, mod)
    exponential_minus_one = [0] + inverse_factorial[1:]
    values = fps_power(exponential_minus_one, column, upper + 1, mod)
    scale = inverse_factorial[column]
    result = [0] * (upper + 1)
    for index in range(column, upper + 1):
        result[index] = values[index] * scale % mod * factorial[index] % mod
    return result


def bernoulli_numbers(max_index, mod=DEFAULT_MOD):
    if max_index < 0:
        return []
    factorial, inverse_factorial = _factorials(max_index + 1, mod)
    series = inverse_factorial[1:max_index + 2]
    values = fps_inverse(series, max_index + 1, mod)
    return [values[index] * factorial[index] % mod
            for index in range(max_index + 1)]


def partition_numbers(max_index, mod=DEFAULT_MOD):
    if max_index < 0:
        return []
    denominator = [0] * (max_index + 1)
    denominator[0] = 1
    index = 1
    while True:
        lower = index * (3 * index - 1) // 2
        if lower > max_index:
            break
        value = -1 if index & 1 else 1
        denominator[lower] = value % mod
        upper = index * (3 * index + 1) // 2
        if upper <= max_index:
            denominator[upper] = value % mod
        index += 1
    return fps_inverse(denominator, max_index + 1, mod)


def bell_numbers(max_index, mod=DEFAULT_MOD):
    if max_index < 0:
        return []
    factorial, inverse_factorial = _factorials(max_index, mod)
    series = [0] + inverse_factorial[1:]
    values = fps_exponential(series, max_index + 1, mod)
    return [values[index] * factorial[index] % mod
            for index in range(max_index + 1)]


def derangement_numbers(max_index, mod=DEFAULT_MOD):
    if max_index < 0:
        return []
    result = [0] * (max_index + 1)
    result[0] = 1
    if max_index:
        result[1] = 0
    for index in range(2, max_index + 1):
        result[index] = (index - 1) * (result[index - 1] + result[index - 2]) % mod
    return result


def sparse_inverse(series, degree=None, mod=DEFAULT_MOD):
    if degree is None:
        degree = len(series)
    if degree < 0:
        raise ValueError("degree must be nonnegative")
    if degree == 0:
        return []
    if not series or series[0] % mod == 0:
        raise ZeroDivisionError("constant coefficient must be invertible")
    inverse_constant = pow(series[0] % mod, -1, mod)
    terms = [(index, value % mod) for index, value in enumerate(series[1:], 1)
             if value % mod]
    result = [0] * degree
    result[0] = inverse_constant
    for index in range(1, degree):
        value = 0
        for offset, coefficient in terms:
            if offset > index:
                break
            value += coefficient * result[index - offset]
        result[index] = -value * inverse_constant % mod
    return result


def sparse_divide(numerator, denominator, degree=None, mod=DEFAULT_MOD):
    if degree is None:
        degree = len(numerator)
    if degree < 0:
        raise ValueError("degree must be nonnegative")
    if not denominator or denominator[0] % mod == 0:
        raise ZeroDivisionError("constant coefficient must be invertible")
    inverse_constant = pow(denominator[0] % mod, -1, mod)
    terms = [(index, value * inverse_constant % mod)
             for index, value in enumerate(denominator[1:], 1) if value % mod]
    result = [0] * degree
    for index in range(degree):
        value = numerator[index] % mod if index < len(numerator) else 0
        value = value * inverse_constant % mod
        for offset, coefficient in terms:
            if offset > index:
                break
            value -= result[index - offset] * coefficient
        result[index] = value % mod
    return result


def sparse_exponential(series, degree=None, mod=DEFAULT_MOD):
    if degree is None:
        degree = len(series)
    if degree == 0:
        return []
    if series and series[0] % mod:
        raise ValueError("constant coefficient must be zero")
    terms = [(index, value % mod) for index, value in enumerate(series[1:], 1)
             if value % mod]
    result = [0] * degree
    result[0] = 1
    for index in range(1, degree):
        value = 0
        for offset, coefficient in terms:
            if offset > index:
                break
            value += offset * coefficient * result[index - offset]
        result[index] = value % mod * pow(index, -1, mod) % mod
    return result


def sparse_logarithm(series, degree=None, mod=DEFAULT_MOD):
    if degree is None:
        degree = len(series)
    if degree == 0:
        return []
    if not series or series[0] % mod != 1:
        raise ValueError("constant coefficient must be one")
    derivative = [index * value % mod for index, value in enumerate(series)][1:]
    quotient = sparse_divide(derivative, series, max(0, degree - 1), mod)
    result = [0] * degree
    for index, value in enumerate(quotient, 1):
        result[index] = value * pow(index, -1, mod) % mod
    return result


def sparse_power(series, exponent, degree=None, mod=DEFAULT_MOD):
    if degree is None:
        degree = len(series)
    if exponent < 0:
        series = sparse_inverse(series, degree, mod)
        exponent = -exponent
    if exponent == 0:
        return [1] + [0] * max(0, degree - 1)
    leading = 0
    while leading < len(series) and series[leading] % mod == 0:
        leading += 1
    shift = leading * exponent
    if leading == len(series) or shift >= degree:
        return [0] * degree
    constant = series[leading] % mod
    inverse_constant = pow(constant, -1, mod)
    normalized = [value * inverse_constant % mod for value in series[leading:]]
    logarithm = sparse_logarithm(normalized, degree - shift, mod)
    factor = exponent % mod
    logarithm = [value * factor % mod for value in logarithm]
    result = sparse_exponential(logarithm, degree - shift, mod)
    scale = pow(constant, exponent, mod)
    return [0] * shift + [value * scale % mod for value in result]


def pascal_transform(values, inverse=False, transpose=False, mod=DEFAULT_MOD):
    """Apply binom(i,j), or its transpose; inverse toggles binomial inversion."""
    size = len(values)
    if size == 0:
        return []
    factorial, inverse_factorial = _factorials(size - 1, mod)
    sign = -1 if inverse else 1
    kernel = [inverse_factorial[index] * (sign if index & 1 else 1) % mod
              for index in range(size)]
    if not transpose:
        scaled = [values[index] * inverse_factorial[index] % mod
                  for index in range(size)]
        product = fps_multiply(scaled, kernel, mod)[:size]
        return [product[index] * factorial[index] % mod for index in range(size)]
    scaled = [values[index] * factorial[index] % mod for index in range(size)]
    scaled.reverse()
    product = fps_multiply(scaled, kernel, mod)[:size]
    product.reverse()
    return [product[index] * inverse_factorial[index] % mod
            for index in range(size)]


def euler_transform(values, mod=DEFAULT_MOD):
    """Coefficients of product((1-x**k)**(-values[k]))."""
    size = len(values)
    logarithm = [0] * size
    for divisor in range(1, size):
        contribution = divisor * values[divisor] % mod
        for multiple in range(divisor, size, divisor):
            logarithm[multiple] += contribution
    for index in range(1, size):
        logarithm[index] = logarithm[index] % mod * pow(index, -1, mod) % mod
    return fps_exponential(logarithm, size, mod)


def circular_series(real_angle, imaginary_angle=None, degree=None, mod=DEFAULT_MOD):
    """Return real/imaginary parts of exp(-imaginary_angle + i*real_angle)."""
    if imaginary_angle is None:
        imaginary_angle = []
    if degree is None:
        degree = max(len(real_angle), len(imaginary_angle))
    if degree == 0:
        return [], []
    if (real_angle and real_angle[0] % mod) or (
        imaginary_angle and imaginary_angle[0] % mod
    ):
        raise ValueError("both constant coefficients must be zero")
    imaginary_unit = modular_square_root(-1, mod)
    if imaginary_unit is not None:
        first = [0] * degree
        second = [0] * degree
        for index in range(degree):
            real = real_angle[index] if index < len(real_angle) else 0
            imaginary = imaginary_angle[index] if index < len(imaginary_angle) else 0
            first[index] = (-imaginary + imaginary_unit * real) % mod
            second[index] = (-imaginary - imaginary_unit * real) % mod
        first = fps_exponential(first, degree, mod)
        second = fps_exponential(second, degree, mod)
        inverse_two = pow(2, -1, mod)
        inverse_two_i = pow(2 * imaginary_unit % mod, -1, mod)
        real = [(left + right) * inverse_two % mod
                for left, right in zip(first, second)]
        imaginary = [(left - right) * inverse_two_i % mod
                     for left, right in zip(first, second)]
        return real, imaginary
    real = [0] * degree
    imaginary = [0] * degree
    real[0] = 1
    for index in range(1, degree):
        real_value = 0
        imaginary_value = 0
        for offset in range(1, index + 1):
            angle_real = real_angle[offset] if offset < len(real_angle) else 0
            angle_imag = imaginary_angle[offset] if offset < len(imaginary_angle) else 0
            scale = offset
            real_value += scale * (
                -angle_imag * real[index - offset]
                - angle_real * imaginary[index - offset]
            )
            imaginary_value += scale * (
                angle_real * real[index - offset]
                - angle_imag * imaginary[index - offset]
            )
        inverse = pow(index, -1, mod)
        real[index] = real_value % mod * inverse % mod
        imaginary[index] = imaginary_value % mod * inverse % mod
    return real, imaginary


def polynomial_mobius_transform(polynomial, a, b, c, d, degree=None,
                                mod=DEFAULT_MOD):
    """Formal expansion of f((a+b*x)/(c+d*x)); requires c != 0."""
    if degree is None:
        degree = len(polynomial)
    c %= mod
    if c == 0:
        raise ValueError("the denominator must have a nonzero constant term")
    denominator_inverse = fps_inverse([c, d % mod], degree, mod)
    inner = fps_multiply([a % mod, b % mod], denominator_inverse, mod)[:degree]
    return fps_compose(polynomial, inner, degree, mod)


sparse_inv = sparse_inverse
sparse_div = sparse_divide
sparse_exp = sparse_exponential
sparse_log = sparse_logarithm
sparse_pow = sparse_power
pascal_matrix = pascal_transform
EulerTransform = euler_transform
