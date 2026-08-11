"""置換とLehmer code・辞書順順位を相互変換する。"""


class _Fenwick:
    __slots__ = ("n", "data")

    def __init__(self, n, ones=False):
        self.n = n
        self.data = [0] * (n + 1)
        if ones:
            for index in range(1, n + 1):
                self.data[index] += 1
                parent = index + (index & -index)
                if parent <= n:
                    self.data[parent] += self.data[index]

    def add(self, index, value):
        index += 1
        while index <= self.n:
            self.data[index] += value
            index += index & -index

    def prefix(self, right):
        result = 0
        while right:
            result += self.data[right]
            right &= right - 1
        return result

    def kth(self, k):
        index = 0
        step = 1 << (self.n.bit_length() - 1) if self.n else 0
        while step:
            candidate = index + step
            if candidate <= self.n and self.data[candidate] <= k:
                index = candidate
                k -= self.data[candidate]
            step >>= 1
        return index


def permutation_to_lehmer(permutation):
    """置換を各位置より右にある小さい値の個数へ変換する。"""
    permutation = list(permutation)
    n = len(permutation)
    if sorted(permutation) != list(range(n)):
        raise ValueError("permutation must contain 0 through n-1 once")
    bit = _Fenwick(n)
    code = [0] * n
    for index in range(n - 1, -1, -1):
        value = permutation[index]
        code[index] = bit.prefix(value)
        bit.add(value, 1)
    return code


def lehmer_to_permutation(code):
    """Lehmer codeを0以上n未満の置換へ戻す。"""
    code = list(code)
    n = len(code)
    for index, digit in enumerate(code):
        if not 0 <= digit < n - index:
            raise ValueError("a Lehmer digit is outside its radix")
    bit = _Fenwick(n, True)
    permutation = [0] * n
    for index, digit in enumerate(code):
        value = bit.kth(digit)
        permutation[index] = value
        bit.add(value, -1)
    return permutation


def permutation_rank(permutation):
    """置換の0-indexed辞書順順位を返す。"""
    code = permutation_to_lehmer(permutation)
    rank = 0
    for index, digit in enumerate(code):
        rank = rank * (len(code) - index) + digit
    return rank


def unrank_permutation(size, rank):
    """size要素の辞書順rank番目の置換を返す。"""
    if size < 0 or rank < 0:
        raise ValueError("size and rank must be nonnegative")
    code = [0] * size
    value = rank
    for radix in range(1, size + 1):
        value, code[size - radix] = divmod(value, radix)
    if value:
        raise IndexError("rank is outside the permutations of this size")
    return lehmer_to_permutation(code)
