import sys

from library_codex.polynomial.MultipointEvaluation import sample_point_shift


read = sys.stdin.buffer.readline
n, m, c = map(int, read().split())
print(" ".join(map(str, sample_point_shift(list(map(int, read().split())), c, m))))
