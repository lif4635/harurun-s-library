import sys

from library_codex.graph.TwoSAT import TwoSAT

read = sys.stdin.buffer.readline
header = read().split()
n, m = int(header[2]), int(header[3])
solver = TwoSAT(n)
for _ in range(m):
    a, b, _ = map(int, read().split())
    solver.add_clause(abs(a) - 1, a > 0, abs(b) - 1, b > 0)
answer = solver.solve()
if answer is None:
    print("s UNSATISFIABLE")
else:
    print("s SATISFIABLE")
    print("v", *(i + 1 if value else -i - 1 for i, value in enumerate(answer)), 0)
