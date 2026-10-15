import sys
from library_codex.polynomial.NewtonBasis998 import to_newton

input = sys.stdin.buffer.readline
n = int(input())
a = list(map(int, input().split()))
p = list(map(int, input().split()))
print(*to_newton(a, p))
