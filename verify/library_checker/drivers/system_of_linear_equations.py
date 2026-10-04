import sys
from library_codex.linear_algebra.Matrix import linear_equation


def main():
    read = sys.stdin.buffer.readline
    n, m = map(int, read().split())
    a = [list(map(int, read().split())) for _ in range(n)]
    result = linear_equation(a, list(map(int, read().split())))
    if result is None:
        print(-1)
    else:
        particular, basis = result
        print(len(basis))
        print(*particular)
        for row in basis:
            print(*row)


if __name__ == "__main__":
    main()
