import sys

from library_codex.geometry.EuclideanMST import euclidean_mst

input = sys.stdin.buffer.readline
n = int(input())
points = [tuple(map(int, input().split())) for _ in range(n)]
sys.stdout.write("\n".join(str(u) + " " + str(v) for u, v in euclidean_mst(points)))
