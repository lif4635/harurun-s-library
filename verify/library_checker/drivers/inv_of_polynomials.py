import sys

from library_codex.polynomial.PolynomialModularPower import polynomial_inverse_mod


read = sys.stdin.buffer.readline
n, m = map(int, read().split())
first = list(map(int, read().split()))
second = list(map(int, read().split()))
try:
    inverse = polynomial_inverse_mod(first, second) if m > 1 else []
except ZeroDivisionError:
    print(-1)
else:
    print(len(inverse))
    print(*inverse)
