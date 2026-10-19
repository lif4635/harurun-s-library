import sys

from library_codex.sequence_structure.SortableArray import SortableArray


def op(first, second):
    a, b = first >> 30, first & 1073741823
    c, d = second >> 30, second & 1073741823
    return (a * c % 998244353 << 30) | ((b * c + d) % 998244353)


read = sys.stdin.buffer.readline
n, q = map(int, read().split())
items = []
for _ in range(n):
    key, a, b = map(int, read().split())
    items.append((key, (a << 30) | b))
data = SortableArray(op, 1 << 30, items)
answers = []
for _ in range(q):
    query = list(map(int, read().split()))
    kind, left, right = query[:3]
    if kind == 0:
        data.set(left, right, (query[3] << 30) | query[4])
    elif kind == 1:
        value = data.prod(left, right)
        answers.append(str(((value >> 30) * query[3] + (value & 1073741823)) % 998244353))
    else:
        data.sort(left, right, kind == 3)
sys.stdout.write('\n'.join(answers) + '\n')
