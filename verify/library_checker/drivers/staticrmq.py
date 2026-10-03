import sys
from library_codex.range_query.StaticRMQ import StaticRMQ

read = sys.stdin.buffer.readline
n, q = map(int, read().split())
table = StaticRMQ(map(int, read().split()))
answers = [str(table.query(*map(int, read().split()))) for _ in range(q)]
sys.stdout.write("\n".join(answers) + "\n")
