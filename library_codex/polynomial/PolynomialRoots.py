"""有限体上で多項式の根を列挙する。"""

from library_codex.polynomial.PolynomialGCD import polynomial_gcd, polynomial_monic
from library_codex.polynomial.PolynomialModularPower import polynomial_pow_mod

from library_codex.fps.FormalPowerSeries import (
    DEFAULT_MOD,
    fps_add,
    fps_derivative,
    fps_divmod,
    fps_inverse,
    fps_logarithm,
    fps_multiply,
    fps_remainder,
    fps_shrink,
    fps_subtract,
    fps_taylor_shift,
)

def _divide_linear(polynomial, root, mod):
    degree = len(polynomial) - 1
    quotient = [0] * degree
    quotient[-1] = polynomial[-1] % mod
    for index in range(degree - 2, -1, -1):
        quotient[index] = (
            polynomial[index + 1] + root * quotient[index + 1]
        ) % mod
    remainder = (polynomial[0] + root * quotient[0]) % mod
    return fps_shrink(quotient, mod), remainder

def polynomial_roots(polynomial, mod=DEFAULT_MOD, multiplicity=False):
    """Find roots in the prime field. The default result has distinct roots."""
    source = fps_shrink(polynomial, mod)
    if not source:
        raise ValueError("the zero polynomial has every field element as a root")
    if len(source) == 1:
        return []
    if mod <= 4096:
        roots = []
        for value in range(mod):
            evaluated = 0
            for coefficient in reversed(source):
                evaluated = (evaluated * value + coefficient) % mod
            if evaluated == 0:
                roots.append(value)
    elif mod == 2:
        roots = []
        if source[0] % 2 == 0:
            roots.append(0)
        if sum(source) & 1 == 0:
            roots.append(1)
    else:
        x = [0, 1]
        linear_part = polynomial_gcd(
            source,
            fps_subtract(polynomial_pow_mod(x, mod, source, mod), x, mod),
            mod,
        )
        roots = []
        stack = [linear_part] if len(linear_part) > 1 else []
        state = 58
        while stack:
            factor = stack.pop()
            if len(factor) == 2:
                roots.append(-factor[0] * pow(factor[1], -1, mod) % mod)
                continue
            split = []
            while len(split) <= 1 or len(split) == len(factor):
                state = (state * 6364136223846793005 + 1442695040888963407) & (
                    (1 << 64) - 1
                )
                candidate = [state % mod, 1]
                half_power = polynomial_pow_mod(
                    candidate, (mod - 1) >> 1, factor, mod
                )
                split = polynomial_gcd(
                    factor, fps_subtract(half_power, [1], mod), mod
                )
            quotient, remainder = fps_divmod(factor, split, mod)
            if remainder:
                raise ArithmeticError("finite-field factor split failed")
            stack.append(polynomial_monic(split, mod))
            stack.append(polynomial_monic(quotient, mod))
        roots.sort()
    if not multiplicity:
        return roots
    answer = []
    remaining = source
    for root in roots:
        while len(remaining) > 1:
            quotient, remainder = _divide_linear(remaining, root, mod)
            if remainder:
                break
            answer.append(root)
            remaining = quotient
    return answer

