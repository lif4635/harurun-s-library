import sys
from library_codex.combinatorial_series.StirlingNumbers import stirling_first_column


def main():
    n, k = map(int, sys.stdin.buffer.readline().split())
    result = stirling_first_column(k, n)
    for i in range(k + 1, n + 1, 2):
        result[i] = -result[i] % 998244353
    sys.stdout.write(" ".join(map(str, result[k:])) + "\n")


if __name__ == "__main__":
    main()
