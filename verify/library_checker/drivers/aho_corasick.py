import sys
from library_codex.string.AhoCorasick import AhoCorasick


def main():
    read = sys.stdin.buffer.readline
    count = int(read())
    tree = AhoCorasick()
    for _ in range(count):
        tree.add(read().strip())
    tree.build()
    answer = [str(len(tree))]
    answer.extend(f"{tree.parent[v]} {tree.failure[v]}" for v in range(1, len(tree)))
    answer.append(" ".join(map(str, tree.pattern_nodes)))
    sys.stdout.write("\n".join(answer))


if __name__ == "__main__":
    main()
