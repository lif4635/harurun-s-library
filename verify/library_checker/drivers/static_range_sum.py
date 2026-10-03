import sys
from itertools import accumulate

read = sys.stdin.buffer.readline
n, q = map(int, read().split())
prefix = [0] + list(accumulate(map(int, read().split())))
answer = []
for _ in range(q):
    left, right = map(int, read().split())
    answer.append(prefix[right] - prefix[left])
print("\n".join(map(str, answer)))
