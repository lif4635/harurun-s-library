"""巨大な10進・16進文字列の商と余りを、同じ進数の文字列で返す。"""

def _number_theory_big_integer_division_parse(value, radix, powers):
    negative = value.startswith('-')
    if value[:1] in ('+', '-'):
        value = value[1:]
    if not value or not value.isascii():
        raise ValueError('expected a signed integer string')
    if radix == 16:
        if value.strip('0123456789abcdefABCDEF'):
            raise ValueError('invalid hexadecimal digit')
        result = int(value, 16)
    else:
        if not value.isdecimal():
            raise ValueError('invalid decimal digit')
        value = value.lstrip('0') or '0'
        chunks = [int(value[max(0, i - 512):i]) for i in range(len(value), 0, -512)]
        level = 0
        while len(chunks) > 1:
            if level == len(powers):
                powers.append(powers[-1] * powers[-1])
            base = powers[level]
            count = len(chunks)
            chunks = [chunks[i] + chunks[i + 1] * base for i in range(0, count - 1, 2)] + ([chunks[-1]] if count & 1 else [])
            level += 1
        result = chunks[0]
    return -result if negative else result

def _number_theory_big_integer_division_decimal(value, powers):
    if not value:
        return '0'
    negative = value < 0
    value = abs(value)
    while powers[-1] <= value:
        powers.append(powers[-1] * powers[-1])
    level = len(powers) - 2
    while level >= 0 and powers[level] > value:
        level -= 1
    stack = [(value, level)]
    output = []
    while stack:
        (current, level) = stack.pop()
        if not current and (not output):
            continue
        if level < 0:
            output.append(str(current).zfill(512) if output else str(current))
        else:
            shift = 512 << level
            reduced = current >> shift
            (high, low) = divmod(reduced, powers[level] >> shift)
            low = (low << shift) + current - (reduced << shift)
            stack.append((low, level - 1))
            stack.append((high, level - 1))
    return ('-' if negative else '') + ''.join(output)

def divide_decimal(first, second):
    """符号付き10進文字列の商・余りを、10進文字列2つで返す。"""
    if max(len(first), len(second)) <= 512:
        (quotient, remainder) = divmod(_number_theory_big_integer_division_parse(first, 10, []), _number_theory_big_integer_division_parse(second, 10, []))
        return (str(quotient), str(remainder))
    powers = [10 ** 512]
    (quotient, remainder) = divmod(_number_theory_big_integer_division_parse(first, 10, powers), _number_theory_big_integer_division_parse(second, 10, powers))
    return (_number_theory_big_integer_division_decimal(quotient, powers), _number_theory_big_integer_division_decimal(remainder, powers))

def divide_hex(first, second):
    """符号付き16進文字列の商・余りを、大文字の16進文字列2つで返す。"""
    (quotient, remainder) = divmod(_number_theory_big_integer_division_parse(first, 16, None), _number_theory_big_integer_division_parse(second, 16, None))
    return (format(quotient, 'X'), format(remainder, 'X'))
import sys

def main():
    read = sys.stdin.readline
    answers = []
    for _ in range(int(read())):
        (first, second) = read().split()
        answers.append(' '.join(divide_decimal(first, second)))
    sys.stdout.write('\n'.join(answers) + '\n')
if __name__ == '__main__':
    main()
