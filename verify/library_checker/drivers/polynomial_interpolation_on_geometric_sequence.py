import sys

from library_codex.polynomial.GeometricMultipointEvaluation import interpolate_geometric


read = sys.stdin.buffer.readline
n, a, r = map(int, read().split())
print(" ".join(map(str, interpolate_geometric(list(map(int, read().split())), a, r))))
