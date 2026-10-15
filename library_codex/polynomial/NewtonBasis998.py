"""998244353上で通常の多項式係数とNewton基底の係数を相互変換する。"""

from library_codex.convolution.NTT998 import MOD, _butterfly, _intt, multiply
from library_codex.fps998.FPS import fps_inv
from library_codex.fps998.MultipointEvaluation import _build_frequency_product_tree


def to_newton(polynomial, points):
    """昇べき順の多項式を、pointsの順で定めるNewton基底へ変換する。"""
    n = len(polynomial)
    if len(points) != n:
        raise ValueError("polynomial and points must have the same length")
    if n == 0:
        return []
    size, products = _build_frequency_product_tree(points)
    root = products[1]
    _intt(root)
    root.append(1)
    root.reverse()
    reversed_polynomial = [0] * (size - n) + [value % MOD for value in reversed(polynomial)]
    current = multiply(reversed_polynomial, fps_inv(root, size))[:size]
    current.extend([0] * (size - len(current)))
    current.reverse()
    answer = [0] * n
    stack = [(1, 0, current)]
    while stack:
        node, start, current = stack.pop()
        width = len(current)
        if width == 1:
            answer[start] = current[0]
            continue
        half = width >> 1
        if start + half < n:
            stack.append((node << 1 | 1, start + half, current[half:]))
        _butterfly(current)
        product = products[node << 1 | 1]
        for i in range(width):
            current[i] = current[i] * product[i] % MOD
        _intt(current)
        stack.append((node << 1, start, current[half:]))
    return answer


def from_newton(coefficients, points):
    """Newton基底の係数を、昇べき順の通常の多項式係数へ戻す。"""
    n = len(coefficients)
    if len(points) != n:
        raise ValueError("coefficients and points must have the same length")
    if n == 0:
        return []
    level = [([-point % MOD, 1], [value % MOD]) for point, value in zip(points, coefficients)]
    while len(level) > 1:
        following = []
        for i in range(0, len(level) - 1, 2):
            left_product, left_value = level[i]
            right_product, right_value = level[i + 1]
            value = multiply(left_product, right_value)
            for j, coefficient in enumerate(left_value):
                value[j] = (value[j] + coefficient) % MOD
            following.append((multiply(left_product, right_product), value))
        if len(level) & 1:
            following.append(level[-1])
        level = following
    return level[0][1]
