import sys
from library_codex.combinatorial_series.BellNumbers import bell_numbers


def main():
    n = int(sys.stdin.buffer.readline())
    result = bell_numbers(n)
    sys.stdout.write(" ".join(map(str, result)) + "\n")


if __name__ == "__main__":
    main()
