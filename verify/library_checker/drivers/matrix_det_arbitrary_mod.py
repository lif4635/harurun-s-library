import sys

from library_codex.linear_algebra.AdvancedMatrix import determinant_arbitrary_mod


def main():
    read = sys.stdin.buffer.readline
    n, mod = map(int, read().split())
    matrix = [list(map(int, read().split())) for _ in range(n)]
    print(determinant_arbitrary_mod(matrix, mod))


if __name__ == "__main__":
    main()
