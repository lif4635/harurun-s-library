import sys

from library_codex.rational.SternBrocotNode import SternBrocotNode


def main():
    read = sys.stdin.buffer.readline
    result = []
    for _ in range(int(read())):
        row = read().split()
        command = row[0]
        if command == b"DECODE_PATH":
            path = [int(row[i + 1]) * (1 if row[i] == b"R" else -1)
                    for i in range(2, len(row), 2)]
            answer = SternBrocotNode(path=path).get()
        elif command == b"ANCESTOR":
            depth, a, b = map(int, row[1:])
            node = SternBrocotNode(a, b)
            answer = node.get() if node.go_parent(node.depth() - depth) else (-1,)
        elif command == b"LCA":
            a, b, c, d = map(int, row[1:])
            answer = SternBrocotNode.lca(SternBrocotNode(a, b), SternBrocotNode(c, d)).get()
        else:
            a, b = map(int, row[1:])
            node = SternBrocotNode(a, b)
            if command == b"RANGE":
                answer = node.lower_bound() + node.upper_bound()
            else:
                answer = [len(node.path)]
                for run in node.path:
                    answer.extend(("R" if run > 0 else "L", abs(run)))
        result.append(" ".join(map(str, answer)))
    sys.stdout.write("\n".join(result))


if __name__ == "__main__":
    main()
