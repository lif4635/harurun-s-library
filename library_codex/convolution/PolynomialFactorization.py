from library_codex.convolution.FormalPowerSeries import (
    DEFAULT_MOD,
    fps_derivative,
    fps_divmod,
    fps_multiply,
    fps_remainder,
    fps_shrink,
    fps_subtract,
)
from library_codex.convolution.PolynomialAlgorithms import (
    polynomial_gcd,
    polynomial_inverse_mod,
    polynomial_monic,
    polynomial_pow_mod,
)


def half_gcd(first, second, mod=DEFAULT_MOD):
    """Monic polynomial gcd; divisions use reversed-FPS Newton inversion."""
    return polynomial_gcd(first, second, mod)


def polynomial_inverse(first, modulus, mod=DEFAULT_MOD):
    try:
        return True, polynomial_inverse_mod(first, modulus, mod)
    except ZeroDivisionError:
        return False, []


def _divide_exact(first, second, mod):
    quotient, remainder = fps_divmod(first, second, mod)
    if fps_shrink(remainder, mod):
        raise ArithmeticError("polynomial division was not exact")
    return polynomial_monic(quotient, mod)


def _square_free_decomposition(polynomial, mod):
    result = []
    pending = [(polynomial_monic(polynomial, mod), 1)]
    while pending:
        source, scale = pending.pop()
        if len(source) <= 1:
            continue
        derivative = fps_shrink(fps_derivative(source, mod), mod)
        if not derivative:
            root = [source[index] for index in range(0, len(source), mod)]
            pending.append((polynomial_monic(root, mod), scale * mod))
            continue
        common = polynomial_gcd(source, derivative, mod)
        remaining = _divide_exact(source, common, mod)
        multiplicity = 1
        while len(remaining) > 1:
            overlap = polynomial_gcd(remaining, common, mod)
            factor = _divide_exact(remaining, overlap, mod)
            if len(factor) > 1:
                result.append((factor, multiplicity * scale))
            remaining = overlap
            common = _divide_exact(common, overlap, mod)
            multiplicity += 1
        if len(common) > 1:
            root = [common[index] for index in range(0, len(common), mod)]
            pending.append((polynomial_monic(root, mod), scale * mod))
    return result


def _equal_degree_factorization(polynomial, degree, mod, state):
    result = []
    stack = [polynomial]
    while stack:
        source = stack.pop()
        source_degree = len(source) - 1
        if source_degree == degree:
            result.append(polynomial_monic(source, mod))
            continue
        split = []
        while len(split) <= 1 or len(split) == len(source):
            random_polynomial = [0] * source_degree
            for index in range(source_degree):
                state[0] = (state[0] * 6364136223846793005
                            + 1442695040888963407) & ((1 << 64) - 1)
                random_polynomial[index] = state[0] % mod
            initial = polynomial_gcd(random_polynomial, source, mod)
            if 1 < len(initial) < len(source):
                split = initial
                break
            if mod == 2:
                trace = []
                power = fps_remainder(random_polynomial, source, mod)
                for _ in range(degree):
                    trace = fps_subtract(trace, power, mod)
                    power = polynomial_pow_mod(power, 2, source, mod)
                split = polynomial_gcd(trace, source, mod)
            else:
                exponent = (pow(mod, degree) - 1) >> 1
                powered = polynomial_pow_mod(
                    random_polynomial, exponent, source, mod
                )
                split = polynomial_gcd(
                    fps_subtract(powered, [1], mod), source, mod
                )
        quotient = _divide_exact(source, split, mod)
        stack.append(polynomial_monic(split, mod))
        stack.append(quotient)
    return result


def _factor_square_free(polynomial, mod, state):
    result = []
    remaining = polynomial_monic(polynomial, mod)
    x = [0, 1]
    frobenius = x
    degree = 1
    while len(remaining) - 1 >= degree * 2:
        frobenius = polynomial_pow_mod(frobenius, mod, remaining, mod)
        common = polynomial_gcd(
            fps_subtract(frobenius, x, mod), remaining, mod
        )
        if len(common) > 1:
            result.extend(_equal_degree_factorization(
                polynomial_monic(common, mod), degree, mod, state
            ))
            remaining = _divide_exact(remaining, common, mod)
            if len(remaining) > 1:
                frobenius = fps_remainder(frobenius, remaining, mod)
        degree += 1
    if len(remaining) > 1:
        result.append(polynomial_monic(remaining, mod))
    return result


def factor_polynomial(polynomial, mod=DEFAULT_MOD, seed=712367821):
    """Factor a polynomial over a prime field, retaining multiplicities."""
    source = fps_shrink(polynomial, mod)
    if not source:
        raise ValueError("the zero polynomial has no finite factorization")
    if len(source) == 1:
        return [source]
    source = polynomial_monic(source, mod)
    state = [seed & ((1 << 64) - 1)]
    result = []
    for square_free, multiplicity in _square_free_decomposition(source, mod):
        factors = _factor_square_free(square_free, mod, state)
        for _ in range(multiplicity):
            result.extend(factor[:] for factor in factors)
    result.sort(key=lambda factor: (len(factor), factor))
    return result


class HalfGCD:
    gcd = staticmethod(half_gcd)
    PolyInv = staticmethod(polynomial_inverse)


FactorizePoly = factor_polynomial
