import sys

from library_codex.tree.ZeroOneTree import min_block_inversions


read = sys.stdin.buffer.readline
n = int(read())
parent = [0] + list(map(int, read().split()))
zero = list(map(int, read().split()))
one = list(map(int, read().split()))
value, order = min_block_inversions(parent, zero, one, return_order=True)
print(value)
print(*order)
