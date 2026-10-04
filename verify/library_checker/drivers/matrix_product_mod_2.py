import sys
from library_codex.linear_algebra.F2Matrix import F2Matrix


def main():
    read = sys.stdin.buffer.readline
    n, m, k = map(int, read().split())
    a = F2Matrix(n, m, [int(read().strip()[::-1], 2) for _ in range(n)])
    b = F2Matrix(m, k, [int(read().strip()[::-1], 2) for _ in range(m)])
    result = a.multiply(b)
    spec = "0" + str(k) + "b"
    sys.stdout.write("\n".join(format(row, spec)[::-1] for row in result.rows) + "\n")


if __name__ == "__main__":
    main()
