import sys

from library_codex.convolution.Convolution64 import convolution_u64


def main():
    data = list(map(int, sys.stdin.buffer.read().split()))
    n = data[0]
    print(*convolution_u64(data[2:2 + n], data[2 + n:]))


if __name__ == "__main__":
    main()
