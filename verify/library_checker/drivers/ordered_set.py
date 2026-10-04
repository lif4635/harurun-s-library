import sys
from library_codex.ordered_set.TreapSet import TreapSet


def main():
    read = sys.stdin.buffer.readline
    n, q = map(int, read().split())
    tree = TreapSet(map(int, read().split()))
    answer = []
    for _ in range(q):
        kind, value = map(int, read().split())
        if kind == 0:
            tree.add(value)
        elif kind == 1:
            tree.discard(value)
        elif kind == 2:
            answer.append(str(tree.kth(value - 1) if value <= len(tree) else -1))
        elif kind == 3:
            answer.append(str(tree.bisect_right(value)))
        elif kind == 4:
            answer.append(str(tree.le(value, -1)))
        else:
            answer.append(str(tree.ge(value, -1)))
    sys.stdout.write("\n".join(answer))


if __name__ == "__main__":
    main()
