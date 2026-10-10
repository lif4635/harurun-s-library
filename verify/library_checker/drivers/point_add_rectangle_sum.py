import sys

from library_codex.spatial_structure.DynamicPointAddRectangleSum import DynamicPointAddRectangleSum


def main():
    read = sys.stdin.buffer.readline
    n, q = map(int, read().split())
    solver = DynamicPointAddRectangleSum()
    for _ in range(n):
        solver.add(*map(int, read().split()))
    for _ in range(q):
        operation = list(map(int, read().split()))
        if operation[0] == 0:
            solver.add(*operation[1:])
        else:
            solver.query(*operation[1:])
    sys.stdout.write("\n".join(map(str, solver.solve())))


if __name__ == "__main__":
    main()
