import sys
from library_codex.fps998.LinearRecurrence import linear_recurrence_nth

read = sys.stdin.buffer.readline
d, k = map(int, read().split())
initial = list(map(int, read().split()))
coefficients = list(map(int, read().split()))
print(linear_recurrence_nth(initial, coefficients, k))
