import sys
from library_codex.string.WildcardPatternMatching import wildcard_pattern_matching


def main():
    text, pattern = sys.stdin.buffer.read().split()
    answer = wildcard_pattern_matching(text, pattern, 42)
    sys.stdout.write("".join(map(str, answer)) + "\n")


if __name__ == "__main__":
    main()
