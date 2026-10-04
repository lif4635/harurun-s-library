import sys
from library_codex.algorithm.SequenceAlgorithms import lis


def main():
    read = sys.stdin.buffer.readline
    n = int(read())
    length, indices, values = lis(map(int, read().split()), restore=True)
    print(length)
    print(*indices)


if __name__ == "__main__":
    main()
