import sys

from library_codex.arithmetic_convolution.MultiplicativeConvolutionModPowerOfTwo import multiplicative_convolution_pow2


def main():
    read = sys.stdin.buffer.readline
    read()
    first = list(map(int, read().split()))
    second = list(map(int, read().split()))
    print(*multiplicative_convolution_pow2(first, second))


if __name__ == "__main__":
    main()
