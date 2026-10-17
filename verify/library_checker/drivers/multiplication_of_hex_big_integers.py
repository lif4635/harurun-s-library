import sys

from library_codex.number_theory.BigIntegerMultiplication import multiply_hex


def main():
    read = sys.stdin.readline
    count = int(read())
    answer = []
    for _ in range(count):
        first, second = read().split()
        answer.append(multiply_hex(first, second))
    sys.stdout.write("\n".join(answer) + "\n")


if __name__ == "__main__":
    main()
