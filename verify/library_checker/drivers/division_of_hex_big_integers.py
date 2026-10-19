import sys

from library_codex.number_theory.BigIntegerDivision import divide_hex


def main():
    read = sys.stdin.readline
    answers = []
    for _ in range(int(read())):
        first, second = read().split()
        answers.append(" ".join(divide_hex(first, second)))
    sys.stdout.write("\n".join(answers) + "\n")


if __name__ == "__main__":
    main()
