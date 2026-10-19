import sys

from library_codex.number_theory.BigIntegerDivision import divide_decimal


def main():
    read = sys.stdin.readline
    answers = []
    for _ in range(int(read())):
        first, second = read().split()
        answers.append(" ".join(divide_decimal(first, second)))
    sys.stdout.write("\n".join(answers) + "\n")


if __name__ == "__main__":
    main()
