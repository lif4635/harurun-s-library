import sys
from bisect import bisect_left

from library_codex.segment_tree.SegTree import SegTree


def compose(first, second):
    a, b = first >> 30, first & 1073741823
    c, d = second >> 30, second & 1073741823
    return (a * c % 998244353) << 30 | ((b * c + d) % 998244353)


read = sys.stdin.buffer.readline
n, q = map(int, read().split())
queries = []
for _ in range(q):
    queries.extend(map(int, read().split()))
positions = sorted({queries[i + 1] for i in range(0, len(queries), 4) if queries[i] == 0})
index = {value: i for i, value in enumerate(positions)}
tree = SegTree(compose, 1 << 30, len(positions))
answer = []
for i in range(0, len(queries), 4):
    if queries[i] == 0:
        tree.set(index[queries[i + 1]], queries[i + 2] << 30 | queries[i + 3])
    else:
        value = tree.prod(bisect_left(positions, queries[i + 1]), bisect_left(positions, queries[i + 2]))
        answer.append(((value >> 30) * queries[i + 3] + (value & 1073741823)) % 998244353)
print("\n".join(map(str, answer)))
