import sys
from library_codex.linear_algebra.Matrix import matrix_determinant


def main():
    read = sys.stdin.buffer.readline
    n = int(read())
    print(matrix_determinant([list(map(int, read().split())) for _ in range(n)]))


if __name__ == "__main__":
    main()
