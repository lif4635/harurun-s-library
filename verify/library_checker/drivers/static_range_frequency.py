import sys
from library_codex.range_query.StaticRangeFrequency import StaticRangeFrequency

read = sys.stdin.buffer.readline
n, q = map(int, read().split())
table = StaticRangeFrequency(map(int, read().split()))
answers = []
for _ in range(q):
    left, right, value = map(int, read().split())
    answers.append(str(table.count(value, left, right)))
sys.stdout.write("\n".join(answers) + "\n")
