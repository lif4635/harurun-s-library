import sys

from library_codex.linear_algebra.Matrix import characteristic_polynomial


def main():
    read = sys.stdin.buffer.readline
    n = int(read())
    matrix = [list(map(int, read().split())) for _ in range(n)]
    print(*characteristic_polynomial(matrix))


if __name__ == "__main__":
    main()
