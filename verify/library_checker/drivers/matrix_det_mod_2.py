import sys
from library_codex.linear_algebra.F2Matrix import F2Matrix


def main():
    read = sys.stdin.buffer.readline
    n = int(read())
    rows = [int(read().strip()[::-1], 2) for _ in range(n)]
    print(F2Matrix(n, n, rows).determinant())


if __name__ == "__main__":
    main()
