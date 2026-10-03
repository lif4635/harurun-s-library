import sys

from library_codex.segment_tree.RangeAffineRangeSum import RangeAffineRangeSum

read = sys.stdin.buffer.readline
n, q = map(int, read().split())
tree = RangeAffineRangeSum(map(int, read().split()), 998244353)
answer = []
for _ in range(q):
    row = list(map(int, read().split()))
    if row[0] == 0:
        tree.apply(row[1], row[2], row[3], row[4])
    else:
        answer.append(tree.range_sum(row[1], row[2]))
print("\n".join(map(str, answer)))
