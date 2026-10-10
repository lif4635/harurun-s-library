import sys

from library_codex.convolution.MinPlusConvolution import minplus_conv_concave

read = sys.stdin.buffer.readline
n, m = map(int, read().split())
a = list(map(int, read().split()))
b = list(map(int, read().split()))
print(" ".join(map(str, minplus_conv_concave(b, a))))
