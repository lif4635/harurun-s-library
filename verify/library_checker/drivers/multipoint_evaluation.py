import sys
from library_codex.fps998.MultipointEvaluation import multipoint_evaluation

read = sys.stdin.buffer.readline
n, m = map(int, read().split())
polynomial = list(map(int, read().split()))
points = list(map(int, read().split()))
print(*multipoint_evaluation(polynomial, points))
