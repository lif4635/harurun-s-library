"""Fast multipoint evaluation over 998244353.

The product tree is kept in NTT form.  During evaluation, the reversed
root polynomial is inverted once and the resulting remainder data is
propagated down the tree.  This avoids a fresh polynomial division at
every node.
"""

from library_codex.convolution.NTT998 import (
    MOD,
    _butterfly,
    _intt,
    multiply,
)
from library_codex.fps998.FPS import fps_inv


def _build_frequency_product_tree(points):
    count = len(points)
    size = 1 << (count - 1).bit_length()
    products = [None] * (size << 1)
    mod = MOD
    for index in range(size):
        value = -points[index] % mod if index < count else 0
        products[size + index] = [
            (value + 1) % mod,
            (value - 1) % mod,
        ]

    for node in range(size - 1, 0, -1):
        left = products[node << 1]
        right = products[node << 1 | 1]
        width = len(left)
        product = [
            (left[index] * right[index] - 1) % mod
            for index in range(width)
        ]
        if node != 1:
            _intt(product)
            product.append(1)
            product.extend([0] * (width - 1))
            _butterfly(product)
        products[node] = product
    return size, products


def multipoint_evaluation(polynomial, points):
    """Return ``polynomial(x)`` for every ``x`` in ``points``.

    The result has ``len(points)`` entries in the same order as the input.
    The implementation is specialized for 998244353.

    Time: ``O((N + M) log^2(N + M))``.
    """

    point_count = len(points)
    if point_count == 0:
        return []
    if not polynomial:
        return [0] * point_count
    if point_count == 1:
        point = points[0] % MOD
        value = 0
        for coefficient in reversed(polynomial):
            value = (value * point + coefficient) % MOD
        return [value]

    size, products = _build_frequency_product_tree(points)
    root = products[1]
    _intt(root)
    root.append(1)
    root.reverse()

    degree = len(polynomial)
    inverse = fps_inv(root, degree)
    inverse.reverse()
    values = multiply(inverse, polynomial)
    values = values[degree - 1:degree - 1 + size]
    values.extend([0] * (size - len(values)))

    result = [0] * point_count
    stack = [(1, 0, size, values)]
    mod = MOD
    while stack:
        node, left, right, current = stack.pop()
        if left >= point_count:
            continue
        if node >= size:
            result[left] = current[0] % mod
            continue

        width = len(current)
        half = width >> 1
        _butterfly(current)
        middle = (left + right) >> 1

        if middle < point_count:
            left_product = products[node << 1]
            right_values = [
                current[index] * left_product[index] % mod
                for index in range(width)
            ]
            _intt(right_values)
            stack.append(
                (node << 1 | 1, middle, right, right_values[half:])
            )

        right_product = products[node << 1 | 1]
        left_values = [
            current[index] * right_product[index] % mod
            for index in range(width)
        ]
        _intt(left_values)
        stack.append((node << 1, left, middle, left_values[half:]))

    return result


def polynomial_interpolation(points, values):
    """Return the polynomial through ``(points[i], values[i])``.

    The result has exactly ``len(points)`` coefficients in ascending order.
    Points must be pairwise distinct modulo 998244353.

    Time: ``O(N log^2 N)``.
    """

    count = len(points)
    if count != len(values):
        raise ValueError("points and values must have the same length")
    if count == 0:
        return []

    size = 1 << (count - 1).bit_length()
    products = [None] * (size << 1)
    for index, point in enumerate(points):
        products[size + index] = [-point % MOD, 1]
    for node in range(size - 1, 0, -1):
        left = products[node << 1]
        right = products[node << 1 | 1]
        if left is None:
            products[node] = right
        elif right is None:
            products[node] = left
        else:
            products[node] = multiply(left, right)
    root = products[1]

    derivative = [
        index * root[index] % MOD
        for index in range(1, len(root))
    ]
    denominators = multipoint_evaluation(derivative, points)
    prefix = [1] * (count + 1)
    for index, denominator in enumerate(denominators):
        if denominator == 0:
            raise ValueError(
                "interpolation points must be distinct modulo 998244353"
            )
        prefix[index + 1] = prefix[index] * denominator % MOD
    inverse = pow(prefix[-1], MOD - 2, MOD)
    coefficients = [None] * (size << 1)
    for index in range(count - 1, -1, -1):
        coefficients[size + index] = [
            values[index] * inverse % MOD * prefix[index] % MOD
        ]
        inverse = inverse * denominators[index] % MOD

    for node in range(size - 1, 0, -1):
        left_node = node << 1
        right_node = left_node | 1
        left = coefficients[left_node]
        right = coefficients[right_node]
        if left is None:
            coefficients[node] = right
            continue
        if right is None:
            coefficients[node] = left
            continue
        merged = multiply(left, products[right_node])
        second = multiply(right, products[left_node])
        if len(merged) < len(second):
            merged.extend([0] * (len(second) - len(merged)))
        for index, value in enumerate(second):
            merged[index] = (merged[index] + value) % MOD
        coefficients[node] = merged
    result = coefficients[1]
    result.extend([0] * (count - len(result)))
    return result[:count]
