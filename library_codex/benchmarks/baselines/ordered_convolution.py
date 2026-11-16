"""i < jを満たす組だけを足す係数畳み込みを998244353上で求める。"""

from library_codex.convolution.NTT998 import MOD, multiply


def ordered_conv(a, b):
    """result[k] = sum(a[i]*b[j] for i+j=k and i<j)を返す。"""
    n, m = len(a), len(b)
    if not n or not m:
        return []
    a = [value % MOD for value in a]
    b = [value % MOD for value in b]
    result = [0] * (n + m - 1)
    stack = [(0, max(n, m))]
    while stack:
        left, right = stack.pop()
        if left >= n or left >= m or right - left <= 1:
            continue
        if right - left <= 32:
            for i in range(left, min(n, right)):
                value = a[i]
                for j in range(i + 1, min(m, right)):
                    result[i + j] += value * b[j]
            continue
        middle = (left + right) >> 1
        if middle < m:
            product = multiply(a[left:min(middle, n)], b[middle:min(right, m)])
            offset = left + middle
            for index, value in enumerate(product):
                result[offset + index] += value
        stack.append((middle, right))
        stack.append((left, middle))
    return [value % MOD for value in result]
