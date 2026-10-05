import sys
from library_codex.graph_matching.Hungarian import hungarian


def main():
    read = sys.stdin.buffer.readline
    costs = [list(map(int, read().split())) for _ in range(int(read()))]
    value, assignment = hungarian(costs)
    print(value)
    print(*assignment)


if __name__ == "__main__":
    main()
