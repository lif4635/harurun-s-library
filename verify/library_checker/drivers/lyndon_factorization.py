import sys
from library_codex.string_sequence.LyndonFactorization import lyndon_factorization


def main():
    factors = lyndon_factorization(sys.stdin.buffer.readline().strip())
    print(0, *(right for left, right in factors))


if __name__ == "__main__":
    main()
