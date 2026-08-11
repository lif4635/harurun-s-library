"""列を辞書順が非増加になるLyndon語へ分解する。"""


def lyndon_factorization(sequence):
    """Duval法で各Lyndon因子の半開区間を返す。"""
    n = len(sequence)
    result = []
    left = 0
    while left < n:
        compare = left
        right = left + 1
        while right < n and sequence[compare] <= sequence[right]:
            if sequence[compare] < sequence[right]:
                compare = left
            else:
                compare += 1
            right += 1
        width = right - compare
        while left <= compare:
            result.append((left, left + width))
            left += width
    return result
