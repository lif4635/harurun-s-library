import sys

from library_codex.algebra.PowerTable import power_table
from library_codex.polynomial.PolynomialExponentialSum import limit_sum_polynomial_exponential

ratio, degree = map(int, sys.stdin.buffer.read().split())
values = power_table(degree, degree, 998244353)
print(limit_sum_polynomial_exponential(values, ratio))
