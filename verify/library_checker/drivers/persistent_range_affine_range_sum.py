import sys

from library_codex.segment_tree.PersistentRangeAffineRangeSum import PersistentRangeAffineRangeSum

input = sys.stdin.buffer.readline
n, q = map(int, input().split())
tree = PersistentRangeAffineRangeSum(map(int, input().split()))
versions = [0] * (q + 1)
answer = []
for i in range(q):
    query = list(map(int, input().split()))
    kind, k = query[:2]
    if kind == 0:
        _, _, left, right, b, c = query
        versions[i + 1] = tree.apply(left, right, b, c, versions[k + 1])
    elif kind == 1:
        _, _, source, left, right = query
        versions[i + 1] = tree.copy(left, right, versions[source + 1], versions[k + 1])
    else:
        _, _, left, right = query
        answer.append(str(tree.prod(left, right, versions[k + 1])))
sys.stdout.write("\n".join(answer))
