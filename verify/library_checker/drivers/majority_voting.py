import sys
from library_codex.range_query.RangeMajority import RangeMajority


def main():
    read = sys.stdin.buffer.readline
    n, q = map(int, read().split())
    table = RangeMajority(map(int, read().split()))
    output = []
    for _ in range(q):
        kind, a, b = map(int, read().split())
        if kind == 0:
            table.set(a, b)
        else:
            result = table.majority(a, b)
            output.append(str(-1 if result is None else result[0]))
    sys.stdout.write("\n".join(output) + "\n")


if __name__ == "__main__":
    main()
