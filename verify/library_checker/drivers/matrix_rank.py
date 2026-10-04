import sys
from library_codex.linear_algebra.Matrix import matrix_rank


def main():
    read = sys.stdin.buffer.readline
    n, m = map(int, read().split())
    print(matrix_rank([list(map(int, read().split())) for _ in range(n)]))


if __name__ == "__main__":
    main()
