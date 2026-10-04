import sys
from library_codex.bitwise_convolution.SetFunction import subset_convolution


def main():
    read = sys.stdin.buffer.readline
    n = int(read())
    a = list(map(int, read().split()))
    b = list(map(int, read().split()))
    result = subset_convolution(a, b)
    sys.stdout.write(" ".join(map(str, result)) + "\n")


if __name__ == "__main__":
    main()
