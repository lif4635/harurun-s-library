import sys

from library_codex.geometry.MinimumEnclosingCircle import minimum_enclosing_circle_boundary

read = sys.stdin.buffer.readline
n = int(read())
points = [tuple(map(int, read().split())) for _ in range(n)]
print("".join(map(str, minimum_enclosing_circle_boundary(points))))
