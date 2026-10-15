import sys

from library_codex.convolution.MultivariateMultiplication import multivariate_multiplication


def main():
    read = sys.stdin.buffer.readline
    dimensions = int(read())
    base = list(map(int, read().split()))
    first = list(map(int, read().split()))
    second = list(map(int, read().split()))
    result = multivariate_multiplication(first, second, base)
    sys.stdout.write(" ".join(map(str, result)) + "\n")


if __name__ == "__main__":
    main()
