import sys
from library_codex.bitwise_convolution.SetFunction import set_series_power_projection


def main():
    read = sys.stdin.buffer.readline
    n, m = map(int, read().split())
    series = list(map(int, read().split()))
    weights = list(map(int, read().split()))
    result = set_series_power_projection(series, weights, m)
    sys.stdout.write(" ".join(map(str, result)) + "\n")


if __name__ == "__main__":
    main()
