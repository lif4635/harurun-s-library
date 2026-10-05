import sys

from library_codex.segment_tree.RangeLinearAddRangeMin import RangeLinearAddRangeMin


def main():
    read = sys.stdin.buffer.readline
    n, q = map(int, read().split())
    table = RangeLinearAddRangeMin(list(map(int, read().split())))
    result = []
    for _ in range(q):
        row = list(map(int, read().split()))
        if row[0] == 0:
            table.add(*row[1:])
        else:
            result.append(str(table.query(row[1], row[2])))
    sys.stdout.write("\n".join(result))


if __name__ == "__main__":
    main()
