import sys
from library_codex.graph_connectivity.BiconnectedComponents import BiconnectedComponents


def main():
    read = sys.stdin.buffer.readline
    n, m = map(int, read().split())
    edges = [tuple(map(int, read().split())) for _ in range(m)]
    groups = BiconnectedComponents(n, edges).components
    answer = [str(len(groups))]
    answer.extend(str(len(group)) + " " + " ".join(map(str, group)) for group in groups)
    sys.stdout.write("\n".join(answer))


if __name__ == "__main__":
    main()
