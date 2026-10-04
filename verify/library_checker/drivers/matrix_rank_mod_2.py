import sys
from library_codex.linear_algebra.F2Matrix import F2Matrix


def main():
    read = sys.stdin.buffer.readline
    n, m = map(int, read().split())
    rows = [int(read().strip()[::-1] or b"0", 2) for _ in range(n)]
    print(F2Matrix(n, m, rows).rank())


if __name__ == "__main__":
    main()
