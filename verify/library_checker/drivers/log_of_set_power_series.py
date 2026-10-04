import sys
from library_codex.bitwise_convolution.SetFunction import set_series_logarithm


def main():
    read = sys.stdin.buffer.readline
    n = int(read())
    a = list(map(int, read().split()))
    result = set_series_logarithm(a)
    sys.stdout.write(" ".join(map(str, result)) + "\n")


if __name__ == "__main__":
    main()
