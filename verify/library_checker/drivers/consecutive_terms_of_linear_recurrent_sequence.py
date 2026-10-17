import sys

from library_codex.fps998.LinearRecurrence import linear_recurrence_slice


def main():
    data = list(map(int, sys.stdin.buffer.read().split()))
    order, start, count = data[:3]
    result = linear_recurrence_slice(data[3:3 + order], data[3 + order:], start, count)
    print(*result)


if __name__ == "__main__":
    main()
