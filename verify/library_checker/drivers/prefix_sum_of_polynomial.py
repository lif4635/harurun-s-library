import sys

from library_codex.polynomial.PolynomialPrefixSum import polynomial_prefix_sum


read = sys.stdin.buffer.readline
n = int(read())
result = polynomial_prefix_sum(list(map(int, read().split())))
result.extend([0] * (n + 1 - len(result)))
print(" ".join(map(str, result)))
