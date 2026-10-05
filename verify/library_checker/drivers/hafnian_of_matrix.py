import sys

from library_codex.linear_algebra.AdvancedMatrix import hafnian


def main():
    read = sys.stdin.buffer.readline
    n = int(read())
    matrix = [list(map(int, read().split())) for _ in range(n)]
    print(hafnian(matrix))


if __name__ == "__main__":
    main()
