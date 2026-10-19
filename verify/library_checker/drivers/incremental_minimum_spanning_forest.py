import sys

from library_codex.graph_spanning.IncrementalMinimumSpanningForest import IncrementalMSF


def main():
    input = sys.stdin.buffer.readline
    n, m = map(int, input().split())
    forest = IncrementalMSF(n)
    answers = []
    for _ in range(m):
        u, v, weight = map(int, input().split())
        answers.append(str(forest.add(u, v, weight)))
    sys.stdout.write(" ".join(answers) + "\n")


if __name__ == "__main__":
    main()
