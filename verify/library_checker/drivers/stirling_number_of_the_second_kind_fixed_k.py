import sys
from library_codex.combinatorial_series.StirlingNumbers import stirling_second_column


def main():
    n, k = map(int, sys.stdin.buffer.readline().split())
    result = stirling_second_column(k, n)
    sys.stdout.write(" ".join(map(str, result[k:])) + "\n")


if __name__ == "__main__":
    main()
