"""Half-GCD internals shared by polynomial GCD and resultant."""

from library_codex.fps.FormalPowerSeries import (
    fps_add,
    fps_multiply,
    fps_shrink,
    fps_subtract,
)
from library_codex.polynomial.PolynomialDivision import poly_divmod


# Below this size the transform matrix costs more than ordinary Euclid on PyPy.
HALF_GCD_THRESHOLD = 192
FAST_GCD_THRESHOLD = 1536


def _identity_matrix():
    return ([1], [], [], [1])


def _multiply(first, second, mod):
    if not first or not second:
        return []
    if len(first) == 1:
        factor = first[0] % mod
        return [] if not factor else [value * factor % mod for value in second]
    if len(second) == 1:
        factor = second[0] % mod
        return [] if not factor else [value * factor % mod for value in first]
    return fps_multiply(first, second, mod)


def _matrix_apply(matrix, pair, mod):
    a00, a01, a10, a11 = matrix
    first, second = pair
    upper = fps_add(
        _multiply(a00, first, mod),
        _multiply(a01, second, mod),
        mod,
    )
    lower = fps_add(
        _multiply(a10, first, mod),
        _multiply(a11, second, mod),
        mod,
    )
    return fps_shrink(upper, mod), fps_shrink(lower, mod)


def _matrix_multiply(left, right, mod):
    """Return left * right for two 2 by 2 polynomial matrices."""

    a00, a01, a10, a11 = left
    b00, b01, b10, b11 = right
    return (
        fps_shrink(fps_add(
            _multiply(a00, b00, mod),
            _multiply(a01, b10, mod),
            mod,
        ), mod),
        fps_shrink(fps_add(
            _multiply(a00, b01, mod),
            _multiply(a01, b11, mod),
            mod,
        ), mod),
        fps_shrink(fps_add(
            _multiply(a10, b00, mod),
            _multiply(a11, b10, mod),
            mod,
        ), mod),
        fps_shrink(fps_add(
            _multiply(a10, b01, mod),
            _multiply(a11, b11, mod),
            mod,
        ), mod),
    )


def _euclid_step(matrix, pair, mod):
    """Perform one exact Euclidean step and update its transform matrix."""

    first, second = pair
    quotient, remainder = poly_divmod(first, second, mod)
    a00, a01, a10, a11 = matrix
    next10 = fps_shrink(
        fps_subtract(a00, _multiply(quotient, a10, mod), mod), mod
    )
    next11 = fps_shrink(
        fps_subtract(a01, _multiply(quotient, a11, mod), mod), mod
    )
    return (a10, a11, next10, next11), (second, remainder), quotient


def _half_gcd(pair, mod):
    """Reduce the second degree below half of the first degree.

    The standard divide-and-conquer formulation is recursive.  This version
    keeps the same states in an explicit stack so library users never depend
    on Python's recursion limit.
    """

    first, second = pair
    stack = [{"state": 0, "first": first, "second": second}]
    result = None
    while stack:
        frame = stack[-1]
        state = frame["state"]
        if state == 0:
            first = frame["first"]
            second = frame["second"]
            size = len(first)
            target = (size + 1) >> 1
            if len(second) <= target:
                result = (_identity_matrix(), [])
                stack.pop()
                continue
            if size <= HALF_GCD_THRESHOLD:
                matrix = _identity_matrix()
                quotients = []
                while second and len(second) > target:
                    matrix, (first, second), quotient = _euclid_step(
                        matrix, (first, second), mod
                    )
                    quotients.append(quotient)
                result = (matrix, quotients)
                stack.pop()
                continue
            frame["state"] = 1
            frame["target"] = target
            stack.append({
                "state": 0,
                "first": first[target:],
                "second": second[target:],
            })
            continue

        if state == 1:
            first_matrix, quotients = result
            first, second = _matrix_apply(
                first_matrix, (frame["first"], frame["second"]), mod
            )
            target = frame["target"]
            if len(second) <= target:
                result = (first_matrix, quotients)
                stack.pop()
                continue
            first_matrix, (first, second), quotient = _euclid_step(
                first_matrix, (first, second), mod
            )
            quotients.append(quotient)
            if not second or len(second) <= target:
                result = (first_matrix, quotients)
                stack.pop()
                continue
            shift = (target << 1) - (len(first) - 1)
            frame["state"] = 2
            frame["first_matrix"] = first_matrix
            frame["quotients"] = quotients
            stack.append({
                "state": 0,
                "first": first[shift:],
                "second": second[shift:],
            })
            continue

        second_matrix, second_quotients = result
        quotients = frame["quotients"]
        quotients.extend(second_quotients)
        result = (
            _matrix_multiply(second_matrix, frame["first_matrix"], mod),
            quotients,
        )
        stack.pop()
    return result


def polynomial_gcd_matrix(first, second, mod):
    """Return M, (g, 0), and Euclid quotients with M*(first, second)=(g,0)."""

    first = fps_shrink(first, mod)
    second = fps_shrink(second, mod)
    matrix = _identity_matrix()
    quotients = []
    while second:
        if len(first) < len(second):
            matrix, (first, second), quotient = _euclid_step(
                matrix, (first, second), mod
            )
            quotients.append(quotient)
            continue
        half_matrix, half_quotients = _half_gcd((first, second), mod)
        if half_matrix != _identity_matrix():
            first, second = _matrix_apply(
                half_matrix, (first, second), mod
            )
            matrix = _matrix_multiply(half_matrix, matrix, mod)
            quotients.extend(half_quotients)
            if not second:
                break
        matrix, (first, second), quotient = _euclid_step(
            matrix, (first, second), mod
        )
        quotients.append(quotient)
    return matrix, (first, second), quotients
