import sys
from library_codex.ordered_set.PointSetRangeFrequency import PointSetRangeFrequency


def main():
    read = sys.stdin.buffer.readline
    n, q = map(int, read().split())
    tree = PointSetRangeFrequency(map(int, read().split()))
    answer = []
    for _ in range(q):
        query = list(map(int, read().split()))
        if query[0] == 0:
            tree.set(query[1], query[2])
        else:
            answer.append(str(tree.query(query[1], query[2], query[3])))
    sys.stdout.write("\n".join(answer))


if __name__ == "__main__":
    main()
