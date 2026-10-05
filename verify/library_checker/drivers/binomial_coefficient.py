import sys

from library_codex.combinatorics.ArbitraryBinomial import ArbitraryModBinomial


read = sys.stdin.buffer.readline
count, mod = map(int, read().split())
table = ArbitraryModBinomial(mod)
result = [str(table.C(*map(int, read().split()))) for _ in range(count)]
sys.stdout.write("\n".join(result))
