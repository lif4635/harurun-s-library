import sys
from library_codex.arithmetic_convolution.MultiplicativeConvolutionModPrime import multiplicative_convolution

input = sys.stdin.buffer.readline
p = int(input())
a = list(map(int, input().split()))
b = list(map(int, input().split()))
print(*multiplicative_convolution(a, b, p))
