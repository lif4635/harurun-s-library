from heapq import heapify, heappop, heappush

from library_codex.convolution.FormalPowerSeries import (
    DEFAULT_MOD,
    fps_add,
    fps_exponential,
    fps_inverse,
    fps_logarithm,
    fps_multiply,
)
from library_codex.convolution.MultipointEvaluation import (
    ProductTree,
    interpolate_consecutive,
)
from library_codex.math.Combinatorics import Combination


def sum_of_rationals(fractions, mod=DEFAULT_MOD):
    """Combine pairs (numerator, denominator) into a single rational FPS."""
    if not fractions:
        return [0], [1]
    heap = []
    for serial, (numerator, denominator) in enumerate(fractions):
        if not denominator:
            raise ZeroDivisionError("a rational FPS denominator is zero")
        numerator = [value % mod for value in numerator]
        denominator = [value % mod for value in denominator]
        heap.append((len(numerator) + len(denominator), serial,
                     numerator, denominator))
    heapify(heap)
    serial = len(heap)
    while len(heap) > 1:
        _, _, first_numerator, first_denominator = heappop(heap)
        _, _, second_numerator, second_denominator = heappop(heap)
        numerator = fps_add(
            fps_multiply(first_numerator, second_denominator, mod),
            fps_multiply(first_denominator, second_numerator, mod),
            mod,
        )
        denominator = fps_multiply(first_denominator, second_denominator, mod)
        heappush(heap, (len(numerator) + len(denominator), serial,
                        numerator, denominator))
        serial += 1
    _, _, numerator, denominator = heap[0]
    return numerator, denominator


def composite_exponential(polynomial, degree, mod=DEFAULT_MOD):
    """Return the first ``degree`` coefficients of f(exp(x))."""
    if degree < 0:
        raise ValueError("degree must be nonnegative")
    if degree == 0:
        return []
    fractions = [
        ([coefficient % mod], [1, -index % mod])
        for index, coefficient in enumerate(polynomial)
    ]
    numerator, denominator = sum_of_rationals(fractions, mod)
    result = fps_multiply(
        numerator,
        fps_inverse(denominator, degree, mod),
        mod,
    )[:degree]
    result.extend([0] * (degree - len(result)))
    inverse_factorial = 1
    for index in range(1, degree):
        inverse_factorial = inverse_factorial * pow(index, -1, mod) % mod
        result[index] = result[index] * inverse_factorial % mod
    return result


def composite_exponential_scaled(polynomial, scale=1, degree=None,
                                 mod=DEFAULT_MOD):
    """Return f(exp(scale*x)) modulo x**degree."""
    if degree is None:
        degree = len(polynomial)
    if scale % mod == 0:
        raise ValueError("scale must be nonzero")
    if degree == 0 or not polynomial:
        return []
    fractions = [
        ([coefficient % mod], [1, -scale * index % mod])
        for index, coefficient in enumerate(polynomial)
    ]
    numerator, denominator = sum_of_rationals(fractions, mod)
    result = fps_multiply(
        numerator, fps_inverse(denominator, degree, mod), mod
    )[:degree]
    result.extend([0] * (degree - len(result)))
    inverse_factorial = 1
    for index in range(1, degree):
        inverse_factorial = inverse_factorial * pow(index, -1, mod) % mod
        result[index] = result[index] * inverse_factorial % mod
    return result


def inverse_composite_exponential(series, scale=1, mod=DEFAULT_MOD):
    """Invert ``composite_exponential_scaled`` for equal input/output size."""
    size = len(series)
    if size == 0:
        return []
    scale %= mod
    if scale == 0:
        raise ValueError("scale must be nonzero")
    moments = [0] * size
    factorial = 1
    for index, value in enumerate(series):
        if index:
            factorial = factorial * index % mod
        moments[index] = value * factorial % mod
    points = [scale * index % mod for index in range(size)]
    tree = ProductTree(points, mod)
    reversed_denominator = tree.polynomial[::-1]
    numerator = fps_multiply(moments, reversed_denominator, mod)[:size]
    evaluations = tree.evaluate(numerator[::-1])
    factorials = [1] * size
    for index in range(1, size):
        factorials[index] = factorials[index - 1] * index % mod
    scale_power = pow(scale, size - 1, mod)
    result = [0] * size
    last = size - 1
    for index in range(size):
        denominator = (scale_power * factorials[index] % mod
                       * factorials[last - index] % mod)
        if (last - index) & 1:
            denominator = -denominator % mod
        result[index] = evaluations[index] * pow(denominator, -1, mod) % mod
    return result


def prefix_sum_polynomial(polynomial, mod=DEFAULT_MOD):
    """Coefficients of g(x)=sum(0 <= y <= x, f(y))."""
    if not polynomial:
        return []
    count = len(polynomial) + 1
    tree = ProductTree(range(count), mod)
    values = tree.evaluate(polynomial)
    for index in range(1, count):
        values[index] = (values[index] + values[index - 1]) % mod
    return tree.interpolate(values)


def product_geometric_substitutions(polynomial, ratio, count,
                                    degree=None, mod=DEFAULT_MOD):
    """Product of f(ratio**k*x), 0 <= k < count, as a truncated FPS."""
    if count < 0:
        raise ValueError("count must be nonnegative")
    if degree is None:
        degree = len(polynomial)
    if degree == 0:
        return []
    if not polynomial or polynomial[0] % mod != 1:
        raise ValueError("the constant coefficient must be one")
    if count == 0:
        return [1] + [0] * (degree - 1)
    logarithm = fps_logarithm(polynomial, degree, mod)
    ratio %= mod
    power = 1
    count_power = 1
    ratio_to_count = pow(ratio, count, mod)
    for index in range(1, degree):
        power = power * ratio % mod
        count_power = count_power * ratio_to_count % mod
        if power == 1:
            multiplier = count % mod
        else:
            multiplier = ((count_power - 1) * pow(power - 1, -1, mod)) % mod
        logarithm[index] = logarithm[index] * multiplier % mod
    return fps_exponential(logarithm, degree, mod)


def multipoint_evaluation_geometric(polynomial, initial, ratio, count,
                                    mod=DEFAULT_MOD):
    """Evaluate f(initial*ratio**i), 0 <= i < count."""
    if count < 0:
        raise ValueError("count must be nonnegative")
    if count == 0:
        return []
    size = len(polynomial)
    if size == 0:
        return [0] * count
    initial %= mod
    ratio %= mod
    if ratio == 0:
        first = 0
        power = 1
        for coefficient in polynomial:
            first = (first + coefficient * power) % mod
            power = power * initial % mod
        return [first] + [polynomial[0] % mod] * (count - 1)
    inverse_ratio = pow(ratio, -1, mod)
    total = size + count - 1
    triangular = [1] * total
    inverse_triangular = [1] * total
    ratio_power = 1
    inverse_power = 1
    for index in range(1, total):
        triangular[index] = triangular[index - 1] * ratio_power % mod
        inverse_triangular[index] = (
            inverse_triangular[index - 1] * inverse_power % mod
        )
        ratio_power = ratio_power * ratio % mod
        inverse_power = inverse_power * inverse_ratio % mod
    weighted = [0] * size
    initial_power = 1
    for index, coefficient in enumerate(polynomial):
        weighted[index] = (
            coefficient * inverse_triangular[index] % mod * initial_power % mod
        )
        initial_power = initial_power * initial % mod
    weighted.reverse()
    product = fps_multiply(weighted, triangular, mod)
    return [
        product[size - 1 + index] * inverse_triangular[index] % mod
        for index in range(count)
    ]


def interpolate_geometric(values, initial, ratio, mod=DEFAULT_MOD):
    """Interpolate f from f(initial*ratio**i); points must be distinct."""
    points = [0] * len(values)
    power = initial % mod
    ratio %= mod
    for index in range(len(values)):
        points[index] = power
        power = power * ratio % mod
    return ProductTree(points, mod).interpolate(values)


def limit_sum_polynomial_exponential(values, ratio, mod=DEFAULT_MOD):
    """Sum ratio**k*f(k), k >= 0, from consecutive samples of f."""
    if not values:
        raise ValueError("at least one sample is required")
    ratio %= mod
    if ratio == 1:
        raise ValueError("the infinite formal sum requires ratio != 1")
    degree = len(values) - 1
    combination = Combination(degree + 1, mod)
    powers = [1] * (degree + 1)
    for index in range(degree):
        powers[index + 1] = powers[index] * ratio % mod
    accumulated = 0
    answer = 0
    for index in range(degree + 1):
        accumulated = (accumulated + powers[index] * values[index]) % mod
        term = (combination.binomial(degree + 1, index + 1)
                * powers[degree - index] % mod * accumulated % mod)
        answer += -term if (degree - index) & 1 else term
    return answer % mod * pow(pow(1 - ratio, degree + 1, mod), -1, mod) % mod


def sum_polynomial_exponential(values, ratio, count, mod=DEFAULT_MOD):
    """Sum ratio**k*f(k), 0 <= k < count, from consecutive samples of f."""
    if not values:
        raise ValueError("at least one sample is required")
    if count <= 0:
        return 0
    ratio %= mod
    degree = len(values) - 1
    powers = [1] * (degree + 1)
    prefixes = [0] * (degree + 1)
    for index in range(degree + 1):
        if index:
            powers[index] = powers[index - 1] * ratio % mod
        prefixes[index] = powers[index] * values[index] % mod
        if index:
            prefixes[index] = (prefixes[index] + prefixes[index - 1]) % mod
    last = count - 1
    if ratio == 0:
        return values[0] % mod
    if ratio == 1:
        return interpolate_consecutive(prefixes, last, mod)
    combination = Combination(degree + 1, mod)
    constant = 0
    for index in range(degree + 1):
        term = (combination.binomial(degree + 1, index + 1)
                * powers[degree - index] % mod * prefixes[index] % mod)
        constant += -term if (degree - index) & 1 else term
    constant %= mod
    constant = constant * pow(pow(1 - ratio, degree + 1, mod), -1, mod) % mod
    inverse_ratio = pow(ratio, -1, mod)
    inverse_power = 1
    adjusted = [0] * (degree + 1)
    for index in range(degree + 1):
        adjusted[index] = (prefixes[index] - constant) * inverse_power % mod
        inverse_power = inverse_power * inverse_ratio % mod
    return (pow(ratio, last, mod)
            * interpolate_consecutive(adjusted, last, mod) + constant) % mod


SumOfRationals = sum_of_rationals
CompExp = composite_exponential
composite_exp = composite_exponential_scaled
inverse_of_composite_exp = inverse_composite_exponential
PrefixSum = prefix_sum_polynomial
ProdOf_f_rk_x = product_geometric_substitutions
MultievalGeomSeq = multipoint_evaluation_geometric
InterpolateGeomSeq = interpolate_geometric
LimitSumOfPolyExp = limit_sum_polynomial_exponential
SumOfPolyExp = sum_polynomial_exponential


def _power_inner_zero_constant(polynomial, weights, count, mod):
    if count < 0:
        raise ValueError("count must be nonnegative")
    if not polynomial or not weights:
        return [0] * (count + 1)
    original_size = len(weights)
    size = 1
    while size < original_size:
        size <<= 1
    product_numerator = [0] * (size << 1)
    denominator = [0] * (size << 1)
    padded_weights = list(weights) + [0] * (size - original_size)
    padded_weights.reverse()
    product_numerator[:size] = [value % mod for value in padded_weights]
    limit = min(len(polynomial), original_size)
    for index in range(1, limit):
        denominator[index] = -polynomial[index] % mod
    block_count = 1
    while size > 1:
        reflected = denominator[:]
        for index in range(1, len(reflected), 2):
            reflected[index] = -reflected[index] % mod
        next_numerator = fps_multiply(product_numerator, reflected, mod)
        next_denominator = fps_multiply(denominator, reflected, mod)
        expanded = size * block_count << 2
        next_numerator.extend([0] * (expanded - len(next_numerator)))
        next_denominator.extend([0] * (expanded - len(next_denominator)))
        offset = size * block_count << 1
        source_length = size * block_count << 1
        for index in range(source_length):
            next_numerator[offset + index] = (
                next_numerator[offset + index] + product_numerator[index]
            ) % mod
            next_denominator[offset + index] = (
                next_denominator[offset + index]
                + denominator[index] + reflected[index]
            ) % mod
        new_length = size * block_count << 1
        new_numerator = [0] * new_length
        new_denominator = [0] * new_length
        half = size >> 1
        for block in range(block_count << 1):
            source = block * size * 2
            destination = block * size
            for index in range(half):
                new_numerator[destination + index] = next_numerator[
                    source + (index << 1) + 1
                ]
                new_denominator[destination + index] = next_denominator[
                    source + (index << 1)
                ]
        product_numerator = new_numerator
        denominator = new_denominator
        size >>= 1
        block_count <<= 1
    result = [product_numerator[index << 1]
              for index in range(block_count)]
    result.reverse()
    result = result[:count + 1]
    result.extend([0] * (count + 1 - len(result)))
    return result


def power_inner_product_enumerate(polynomial, weights, count,
                                  mod=DEFAULT_MOD):
    """Enumerate sum_j weights[j]*[x^j] polynomial(x)^i."""
    if count < 0:
        raise ValueError("count must be nonnegative")
    if not polynomial or not weights:
        return [0] * (count + 1)
    constant = polynomial[0] % mod
    shifted = list(polynomial)
    shifted[0] = 0
    result = _power_inner_zero_constant(shifted, weights, count, mod)
    if constant:
        factorial = [1] * (count + 1)
        inverse_factorial = [1] * (count + 1)
        for index in range(1, count + 1):
            factorial[index] = factorial[index - 1] * index % mod
        inverse_factorial[count] = pow(factorial[count], -1, mod)
        for index in range(count, 0, -1):
            inverse_factorial[index - 1] = (
                inverse_factorial[index] * index % mod
            )
        coefficient = [0] * (count + 1)
        power = 1
        for index in range(count + 1):
            result[index] = result[index] * inverse_factorial[index] % mod
            coefficient[index] = inverse_factorial[index] * power % mod
            power = power * constant % mod
        result = fps_multiply(result, coefficient, mod)[:count + 1]
        result.extend([0] * (count + 1 - len(result)))
        return [result[index] * factorial[index] % mod
                for index in range(count + 1)]
    return result


def power_coefficient_enumerate(polynomial, multiplier=None, count=None,
                                mod=DEFAULT_MOD):
    """Enumerate [x^n] polynomial(x)^i*multiplier(x), n=len(f)-1."""
    degree = len(polynomial) - 1
    if degree < 0:
        if count is None:
            count = 0
        return [0] * (count + 1)
    if multiplier is None:
        multiplier = [1]
    if count is None:
        count = degree
    weights = [0] * (degree + 1)
    for exponent in range(degree + 1):
        multiplier_index = degree - exponent
        if multiplier_index < len(multiplier):
            weights[exponent] = multiplier[multiplier_index]
    return power_inner_product_enumerate(polynomial, weights, count, mod)


PowEnumerate = power_inner_product_enumerate
pow_enumerate = power_coefficient_enumerate
