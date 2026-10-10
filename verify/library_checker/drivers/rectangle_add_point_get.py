import sys

from library_codex.spatial_structure.RectangleAddPointGet import RectangleAddPointGet


def main():
    read = sys.stdin.buffer.readline
    n, q = map(int, read().split())
    initial = [tuple(map(int, read().split())) for _ in range(n)]
    operations = [tuple(map(int, read().split())) for _ in range(q)]
    solver = RectangleAddPointGet((op[1], op[2]) for op in operations if op[0])
    for rectangle in initial:
        solver.add(*rectangle)
    answers = []
    for operation in operations:
        if operation[0] == 0:
            solver.add(*operation[1:])
        else:
            answers.append(solver.get(operation[1], operation[2]))
    sys.stdout.write("\n".join(map(str, answers)))


if __name__ == "__main__":
    main()
