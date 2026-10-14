import sys

from library_codex.convolution.NTT import convolution_any_mod


def main():
    read = sys.stdin.buffer.readline
    n, m = map(int, read().split())
    first = list(map(int, read().split()))
    second = list(map(int, read().split()))
    result = convolution_any_mod(first, second, 1000000007)
    sys.stdout.write(" ".join(map(str, result)) + "\n")


if __name__ == "__main__":
    main()
