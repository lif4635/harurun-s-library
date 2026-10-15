import sys

from library_codex.convolution.MultidimensionalDFT import multivariate_circular_convolution


def main():
    read = sys.stdin.buffer.readline
    mod, dimensions = map(int, read().split())
    base = list(map(int, read().split()))
    first = list(map(int, read().split()))
    second = list(map(int, read().split()))
    result = multivariate_circular_convolution(first, second, base, mod)
    sys.stdout.write(" ".join(map(str, result)) + "\n")


if __name__ == "__main__":
    main()
