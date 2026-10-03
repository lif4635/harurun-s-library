import sys
from library_codex.convolution.MinPlusConvolution import minplus_conv_convex

read = sys.stdin.buffer.readline
n, m = map(int, read().split())
first = list(map(int, read().split()))
second = list(map(int, read().split()))
print(*minplus_conv_convex(first, second))
