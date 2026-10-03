import sys

from library_codex.geometry.ConvexFurthest import furthest_neighbors

read = sys.stdin.buffer.readline
for _ in range(int(read())):
    points = [tuple(map(int, read().split())) for _ in range(int(read()))]
    print(*furthest_neighbors(points))
