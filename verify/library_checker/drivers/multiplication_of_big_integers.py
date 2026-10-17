import sys

from library_codex.number_theory.BigIntegerMultiplication import multiply_decimal


def main():
    read = sys.stdin.readline
    count = int(read())
    answer = []
    for _ in range(count):
        first, second = read().split()
        answer.append(multiply_decimal(first, second))
    sys.stdout.write("\n".join(answer) + "\n")


if __name__ == "__main__":
    main()
