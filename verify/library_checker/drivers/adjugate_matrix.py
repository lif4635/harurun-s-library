import sys

from library_codex.linear_algebra.Adjugate import adjugate


def main():
    read = sys.stdin.buffer.readline
    n = int(read())
    matrix = [list(map(int, read().split())) for _ in range(n)]
    result = adjugate(matrix)
    sys.stdout.write("\n".join(" ".join(map(str, row)) for row in result) + "\n")


if __name__ == "__main__":
    main()
