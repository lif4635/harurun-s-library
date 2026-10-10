import sys

from library_codex.spatial_structure.RectangleAddRectangleSum import RectangleAddRectangleSum


def main():
    read = sys.stdin.buffer.readline
    n, q = map(int, read().split())
    solver = RectangleAddRectangleSum()
    for _ in range(n):
        solver.add(*map(int, read().split()))
    for _ in range(q):
        solver.query(*map(int, read().split()))
    sys.stdout.write("\n".join(map(str, solver.solve(998244353))))


if __name__ == "__main__":
    main()
