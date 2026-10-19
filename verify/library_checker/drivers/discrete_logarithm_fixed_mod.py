import sys

from library_codex.number_theory.FixedDiscreteLog import FixedDiscreteLog


def main():
    read = sys.stdin.buffer.readline
    prime, root, count = map(int, read().split())
    log = FixedDiscreteLog(prime, root)
    sys.stdout.write("\n".join(str(log(int(read()))) for _ in range(count)) + "\n")


if __name__ == "__main__":
    main()
