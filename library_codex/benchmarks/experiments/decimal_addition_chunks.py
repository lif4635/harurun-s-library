import sys


def _decimal_parts(value):
    negative = value.startswith("-")
    if value[:1] in ("+", "-"):
        value = value[1:]
    if not value or not value.isascii() or not value.isdecimal():
        raise ValueError("expected a signed decimal string")
    return negative, value.lstrip("0") or "0"


def add_decimal(first, second):
    negative, first = _decimal_parts(first)
    other_negative, second = _decimal_parts(second)
    if (len(first), first) < (len(second), second):
        first, second = second, first
        negative, other_negative = other_negative, negative
    direction = 1 if negative == other_negative else -1
    if direction < 0 and first == second:
        return "0"
    i, j = len(first), len(second)
    carry = 0
    parts = []
    while i:
        left = max(0, i - 9)
        right = max(0, j - 9)
        value = int(first[left:i]) + carry
        if j:
            value += direction * int(second[right:j])
        carry, digit = divmod(value, 1000000000)
        parts.append(str(digit).zfill(9))
        i, j = left, right
    if carry:
        parts.append(str(carry))
    result = "".join(reversed(parts)).lstrip("0") or "0"
    return "-" + result if negative and result != "0" else result


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
