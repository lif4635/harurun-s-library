import sys
from library_codex.bitwise_convolution.SetFunction import bitwise_and_convolution

read = sys.stdin.buffer.readline
n = int(read())
first = list(map(int, read().split()))
second = list(map(int, read().split()))
print(*bitwise_and_convolution(first, second))
