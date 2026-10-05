import sys


def main():
    read = sys.stdin.buffer.readline
    write = sys.stdout.write
    count = int(read())
    while count:
        size = min(count, 8192)
        answer = []
        for _ in range(size):
            a, b = map(int, read().split())
            answer.append(str(a + b))
        write("\n".join(answer) + "\n")
        count -= size


if __name__ == "__main__":
    main()
