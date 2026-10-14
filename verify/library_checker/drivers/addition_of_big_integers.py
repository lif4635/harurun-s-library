import sys

from library_codex.number_theory.DecimalAddition import add_decimal


def main():
    read = sys.stdin.buffer.readline
    count = int(read())
    answer = []
    for _ in range(count):
        first, second = read().decode().split()
        answer.append(add_decimal(first, second))
    sys.stdout.write("\n".join(answer) + "\n")


if __name__ == "__main__":
    main()
