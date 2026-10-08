import sys

from library_codex.segment_tree.LazySegTree import LazySegTree


def op(first, second):
    value = first + second
    return value if value < (998244353 << 30) else value - (998244353 << 30)


def mapping(action, value, length):
    a, b = action >> 30, action & 1073741823
    width = value & 1073741823
    return ((a * (value >> 30) + b * width) % 998244353) << 30 | width


def composition(new, old):
    a, b = new >> 30, new & 1073741823
    c, d = old >> 30, old & 1073741823
    return (a * c % 998244353) << 30 | ((a * d + b) % 998244353)


read = sys.stdin.buffer.readline
n, q = map(int, read().split())
queries = [list(map(int, read().split())) for _ in range(q)]
points = sorted({point for row in queries for point in row[1:3]})
index = {value: i for i, value in enumerate(points)}
values = [points[i + 1] - points[i] for i in range(len(points) - 1)]
tree = LazySegTree(op, 0, mapping, composition, 1 << 30, values)
answer = []
for row in queries:
    left, right = index[row[1]], index[row[2]]
    if row[0] == 0:
        tree.apply(left, right, row[3] << 30 | row[4])
    else:
        answer.append(tree.prod(left, right) >> 30)
print("\n".join(map(str, answer)))
