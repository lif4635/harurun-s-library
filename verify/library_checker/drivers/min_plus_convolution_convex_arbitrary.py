import sys
from library_codex.convolution.MinPlusConvolution import minplus_conv

read = sys.stdin.buffer.readline
n, m = map(int, read().split())
convex = list(map(int, read().split()))
arbitrary = list(map(int, read().split()))
print(*minplus_conv(arbitrary, convex))
