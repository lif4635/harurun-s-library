import sys
from library_codex.linear_algebra.AdvancedMatrix import directed_spanning_tree_count


def main():
    read = sys.stdin.buffer.readline
    n, m, root = map(int, read().split())
    edges = [(*map(int, read().split()), 1) for _ in range(m)]
    print(directed_spanning_tree_count(n, edges, root, inward=False))


if __name__ == "__main__":
    main()
