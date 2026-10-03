import sys

from library_codex.polynomial.PolynomialDivision998 import poly_divmod

read = sys.stdin.buffer.readline
n, m = map(int, read().split())
first = list(map(int, read().split()))
second = list(map(int, read().split()))
quotient, remainder = poly_divmod(first, second)
print(len(quotient), len(remainder))
print(*quotient)
print(*remainder)
