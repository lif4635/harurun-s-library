import sys
from library_codex.string.RunEnumeration import run_enumerate


def main():
    runs = run_enumerate(sys.stdin.buffer.readline().strip())
    answer = [str(len(runs))]
    answer.extend(f"{period} {left} {right}" for period, left, right in runs)
    sys.stdout.write("\n".join(answer))


if __name__ == "__main__":
    main()
