import sys

from library_codex.polynomial.PolynomialRoots import polynomial_roots


read = sys.stdin.buffer.readline
degree = int(read())
roots = polynomial_roots(list(map(int, read().split())))
print(len(roots))
print(*roots)
