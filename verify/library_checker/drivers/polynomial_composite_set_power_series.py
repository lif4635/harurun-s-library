import sys
from library_codex.bitwise_convolution.SetFunction import set_series_composition


def main():
    read = sys.stdin.buffer.readline
    m, n = map(int, read().split())
    outer = list(map(int, read().split()))
    series = list(map(int, read().split()))
    result = set_series_composition(outer, series)
    sys.stdout.write(" ".join(map(str, result)) + "\n")


if __name__ == "__main__":
    main()
