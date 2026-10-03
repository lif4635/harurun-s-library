import sys
from library_codex.fps998.MultipointEvaluation import polynomial_interpolation

read = sys.stdin.buffer.readline
n = int(read())
points = list(map(int, read().split()))
values = list(map(int, read().split()))
print(*polynomial_interpolation(points, values))
