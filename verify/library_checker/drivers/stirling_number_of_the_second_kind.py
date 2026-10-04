import sys
from library_codex.combinatorial_series.StirlingNumbers import stirling_second_row


def main():
    n = int(sys.stdin.buffer.readline())
    result = stirling_second_row(n)
    sys.stdout.write(" ".join(map(str, result)) + "\n")


if __name__ == "__main__":
    main()
