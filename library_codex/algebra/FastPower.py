"""同じ底や指数で繰り返す累乗計算を前計算で高速化する。"""

class FastPower:
    """Fixed-base powers with O(number of exponent blocks) queries."""

    __slots__ = ("mod", "block_bits", "mask", "tables", "identity")

    def __init__(self, base, mod, max_exponent=(1 << 63) - 1, block_bits=10):
        if mod <= 0 or max_exponent < 0 or block_bits <= 0:
            raise ValueError("invalid fixed-power parameters")
        self.mod = mod
        self.block_bits = block_bits
        width = 1 << block_bits
        self.mask = width - 1
        self.identity = 1 % mod
        blocks = max(1, (max_exponent.bit_length() + block_bits - 1) // block_bits)
        tables = []
        current_base = base % mod
        for _ in range(blocks):
            table = [self.identity] * width
            for index in range(1, width):
                table[index] = table[index - 1] * current_base % mod
            tables.append(table)
            current_base = table[-1] * current_base % mod
        self.tables = tables

    def __call__(self, exponent):
        if exponent < 0 or exponent.bit_length() > len(self.tables) * self.block_bits:
            raise ValueError("exponent is outside the precomputed range")
        result = self.identity
        shift = 0
        while exponent:
            result = result * self.tables[shift][exponent & self.mask] % self.mod
            exponent >>= self.block_bits
            shift += 1
        return result

