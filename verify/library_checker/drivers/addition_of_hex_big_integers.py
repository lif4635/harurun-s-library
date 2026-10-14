import sys


def main():
    read = sys.stdin.buffer.readline
    count = int(read())
    answer = []
    for _ in range(count):
        first, second = read().split()
        answer.append(format(int(first, 16) + int(second, 16), "X"))
    sys.stdout.write("\n".join(answer) + "\n")


if __name__ == "__main__":
    main()
