import sys

from library_codex.string.DequePalindromicTree import DequePalindromicTree


def main():
    read = sys.stdin.buffer.readline
    q = int(read())
    tree = DequePalindromicTree()
    answer = []
    for _ in range(q):
        line = read()
        operation = line[0]
        if operation == 48:
            tree.appendleft(line[2])
        elif operation == 49:
            tree.append(line[2])
        elif operation == 50:
            tree.popleft()
        else:
            tree.pop()
        a, b, c = tree.query()
        answer.append(f"{a} {b} {c}")
    sys.stdout.write("\n".join(answer))


if __name__ == "__main__":
    main()
