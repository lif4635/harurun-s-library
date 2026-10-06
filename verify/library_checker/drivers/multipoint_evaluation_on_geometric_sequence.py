import sys

from library_codex.polynomial.GeometricMultipointEvaluation import multipoint_evaluation_geometric


read = sys.stdin.buffer.readline
n, m, a, r = map(int, read().split())
print(" ".join(map(str, multipoint_evaluation_geometric(list(map(int, read().split())), a, r, m))))
