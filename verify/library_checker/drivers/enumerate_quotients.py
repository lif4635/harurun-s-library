import sys
from library_codex.number_theory.EnumerateQuotient import enumerate_quotient


def main():
    values = [value for value, left, right in enumerate_quotient(int(sys.stdin.buffer.readline()))]
    print(len(values))
    sys.stdout.write(" ".join(map(str, reversed(values))) + "\n")


if __name__ == "__main__":
    main()
