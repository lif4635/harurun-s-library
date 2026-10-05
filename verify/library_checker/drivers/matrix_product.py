import sys

from library_codex.linear_algebra.Strassen import strassen_matrix_multiply


def main():
    read = sys.stdin.buffer.readline
    n, m, k = map(int, read().split())
    first = [list(map(int, read().split())) for _ in range(n)]
    second = [list(map(int, read().split())) for _ in range(m)]
    product = strassen_matrix_multiply(first, second)
    sys.stdout.write('\n'.join(' '.join(map(str, row)) for row in product))


if __name__ == "__main__":
    main()
