import sys
from library_codex.range_query.StaticRangeDistinct import StaticRangeDistinct

read = sys.stdin.buffer.readline
n, q = map(int, read().split())
table = StaticRangeDistinct(map(int, read().split()))
answers = [str(table.count(*map(int, read().split()))) for _ in range(q)]
sys.stdout.write("\n".join(answers) + "\n")
