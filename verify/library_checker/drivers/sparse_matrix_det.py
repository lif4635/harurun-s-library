import sys

from library_codex.linear_algebra.BlackBoxLinearAlgebra import SparseMatrix, black_box_determinant


def main():
    read = sys.stdin.buffer.readline
    n, m = map(int, read().split())
    matrix = SparseMatrix(n)
    for _ in range(m):
        row, column, value = map(int, read().split())
        matrix.add(row, column, value)
    print(black_box_determinant(matrix, seed=20261005))


if __name__ == "__main__":
    main()
