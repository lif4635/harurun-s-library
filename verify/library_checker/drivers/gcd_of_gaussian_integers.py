import sys
from library_codex.number_theory.GaussianInteger import GaussianInteger, gaussian_gcd


def main():
    read = sys.stdin.buffer.readline
    answer = []
    for _ in range(int(read())):
        a, b, c, d = map(int, read().split())
        value = gaussian_gcd(GaussianInteger(a, b), GaussianInteger(c, d))
        answer.append(f"{value.real} {value.imag}")
    sys.stdout.write("\n".join(answer))


if __name__ == "__main__":
    main()
