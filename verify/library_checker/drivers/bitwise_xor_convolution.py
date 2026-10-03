import sys
from library_codex.bitwise_convolution.SetFunction import bitwise_xor_convolution

read = sys.stdin.buffer.readline
n = int(read())
first = list(map(int, read().split()))
second = list(map(int, read().split()))
print(*bitwise_xor_convolution(first, second))
