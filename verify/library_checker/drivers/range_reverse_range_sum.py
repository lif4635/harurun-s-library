import sys
from library_codex.sequence_structure.ImplicitTreap import ImplicitTreap


def main():
    read = sys.stdin.buffer.readline
    n, q = map(int, read().split())
    tree = ImplicitTreap(map(int, read().split()), commutative=True)
    answer = []
    for _ in range(q):
        kind, left, right = map(int, read().split())
        if kind == 0:
            tree.reverse_range(left, right)
        else:
            answer.append(str(tree.prod(left, right)))
    sys.stdout.write("\n".join(answer))


if __name__ == "__main__":
    main()
