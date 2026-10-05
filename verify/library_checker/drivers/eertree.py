import sys
from library_codex.string.PalindromicTree import PalindromicTree


def main():
    tree = PalindromicTree(sys.stdin.buffer.readline().strip())
    answer = [str(tree.distinct_count)]
    answer.extend(f"{tree.parent[v] - 1} {tree.link[v] - 1}" for v in range(2, len(tree)))
    answer.append(" ".join(str(v - 1) for v in tree.suffix_states))
    sys.stdout.write("\n".join(answer))


if __name__ == "__main__":
    main()
