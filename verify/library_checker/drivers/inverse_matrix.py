import sys
from library_codex.linear_algebra.Matrix import inverse_matrix


def main():
    read = sys.stdin.buffer.readline
    n = int(read())
    result = inverse_matrix([list(map(int, read().split())) for _ in range(n)])
    if result is None:
        print(-1)
    else:
        sys.stdout.write("\n".join(" ".join(map(str, row)) for row in result) + "\n")


if __name__ == "__main__":
    main()
