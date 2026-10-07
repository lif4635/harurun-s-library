import sys

from library_codex.linear_algebra.F2Matrix import F2Matrix

read = sys.stdin.buffer.readline
n, m = map(int, read().split())
rows = [int(read().strip()[::-1], 2) for _ in range(n)]
rhs = int(read().strip()[::-1], 2)
answer = F2Matrix(n, m, rows).solve(rhs)
if answer is None:
    print(-1)
else:
    particular, kernel = answer
    spec = "0" + str(m) + "b"
    print(len(kernel))
    print(format(particular, spec)[::-1])
    sys.stdout.write("".join(format(value, spec)[::-1] + "\n" for value in kernel))
