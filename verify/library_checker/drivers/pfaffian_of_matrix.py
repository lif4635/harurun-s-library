import sys

from library_codex.linear_algebra.AdvancedMatrix import pfaffian


def main():
    read = sys.stdin.buffer.readline
    n = 2 * int(read())
    matrix = [list(map(int, read().split())) for _ in range(n)]
    print(pfaffian(matrix))


if __name__ == "__main__":
    main()
