import sys

from library_codex.linear_algebra.Frobenius import Frobenius


def main():
    read = sys.stdin.buffer.readline
    n, exponent = map(int, read().split())
    matrix = [list(map(int, read().split())) for _ in range(n)]
    product = Frobenius(matrix).pow(exponent)
    sys.stdout.write('\n'.join(' '.join(map(str, row)) for row in product))


if __name__ == "__main__":
    main()
