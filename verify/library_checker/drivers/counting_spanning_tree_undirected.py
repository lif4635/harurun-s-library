import sys
from library_codex.linear_algebra.AdvancedMatrix import spanning_tree_count


def main():
    read = sys.stdin.buffer.readline
    n, m = map(int, read().split())
    edges = [tuple(map(int, read().split())) for _ in range(m)]
    print(spanning_tree_count(n, edges))


if __name__ == "__main__":
    main()
