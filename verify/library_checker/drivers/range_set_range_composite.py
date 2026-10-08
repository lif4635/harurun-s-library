import sys

from library_codex.segment_tree.RangeAssignSegTree import RangeAssignSegTree


def op(first, second):
    a, b = first >> 30, first & 1073741823
    c, d = second >> 30, second & 1073741823
    return (a * c % 998244353) << 30 | ((b * c + d) % 998244353)


read = sys.stdin.buffer.readline
n, q = map(int, read().split())
values = []
for _ in range(n):
    a, b = map(int, read().split())
    values.append(a << 30 | b)
tree = RangeAssignSegTree(op, 1 << 30, values)
answer = []
for _ in range(q):
    row = list(map(int, read().split()))
    if row[0] == 0:
        tree.assign(row[1], row[2], row[3] << 30 | row[4])
    else:
        value = tree.prod(row[1], row[2])
        answer.append(((value >> 30) * row[3] + (value & 1073741823)) % 998244353)
print("\n".join(map(str, answer)))
