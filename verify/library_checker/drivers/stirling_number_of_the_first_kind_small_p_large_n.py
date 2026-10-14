import sys

from library_codex.combinatorics.StirlingNumberQuery import StirlingNumberQuery


def main():
    read = sys.stdin.buffer.readline
    t, p = map(int, read().split())
    query = StirlingNumberQuery(p).first_kind
    result = []
    for _ in range(t):
        n, k = map(int, read().split())
        result.append(str(query(n, k)))
    sys.stdout.write("\n".join(result))


if __name__ == "__main__":
    main()
