import sys

from library_codex.combinatorics.QBinomial import QBinomial


read = sys.stdin.buffer.readline
count, mod, q = map(int, read().split())
data = list(map(int, sys.stdin.buffer.read().split()))
maximum = max(data[::2], default=0)
table = QBinomial(q, maximum, mod)
result = [str(table.C(data[i], data[i + 1])) for i in range(0, count * 2, 2)]
sys.stdout.write("\n".join(result))
