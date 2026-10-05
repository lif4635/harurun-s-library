import sys
from library_codex.string.PrefixSubstringLCS import PrefixSubstringLCS


def main():
    read = sys.stdin.buffer.readline
    count = int(read())
    first = read().strip()
    second = read().strip()
    solver = PrefixSubstringLCS(first, second)
    for _ in range(count):
        solver.add(*map(int, read().split()))
    sys.stdout.write("\n".join(map(str, solver.run())))


if __name__ == "__main__":
    main()
