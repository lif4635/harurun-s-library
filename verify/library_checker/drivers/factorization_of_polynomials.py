import sys
from collections import Counter

from library_codex.polynomial.PolynomialFactorization import factor_polynomial


read = sys.stdin.buffer.readline
degree, mod = map(int, read().split())
polynomial = list(map(int, read().split()))
factors = Counter(map(tuple, factor_polynomial(polynomial, mod))) if degree else {}
print(len(factors))
for factor, multiplicity in factors.items():
    print(multiplicity, len(factor) - 1, *factor)
