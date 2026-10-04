import sys
from library_codex.linear_algebra.F2Matrix import F2Matrix


def main():
    read = sys.stdin.buffer.readline
    n = int(read())
    rows = [int(read().strip()[::-1], 2) for _ in range(n)]
    result = F2Matrix(n, n, rows).inverse()
    if result is None:
        print(-1)
    else:
        spec = "0" + str(n) + "b"
        sys.stdout.write("\n".join(format(row, spec)[::-1] for row in result.rows) + "\n")


if __name__ == "__main__":
    main()
