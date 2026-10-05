import sys

from library_codex.linear_algebra.Matrix import matrix_power


def main():
    read = sys.stdin.buffer.readline
    n, exponent = map(int, read().split())
    matrix = [list(map(int, read().split())) for _ in range(n)]
    product = matrix_power(matrix, exponent)
    sys.stdout.write('\n'.join(' '.join(map(str, row)) for row in product))


if __name__ == "__main__":
    main()
