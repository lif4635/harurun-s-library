class BinaryTrie:
    __slots__ = ("bit_length", "left", "right", "count", "lazy")

    def __init__(self, bit_length=30):
        if bit_length <= 0:
            raise ValueError("bit_length must be positive")
        self.bit_length = bit_length
        self.left = [-1]
        self.right = [-1]
        self.count = [0]
        self.lazy = 0

    def add(self, value, amount=1):
        if amount <= 0:
            return
        value ^= self.lazy
        node = 0
        self.count[node] += amount
        left = self.left
        right = self.right
        count = self.count
        for bit in range(self.bit_length - 1, -1, -1):
            direction = value >> bit & 1
            child = right[node] if direction else left[node]
            if child < 0:
                child = len(count)
                left.append(-1)
                right.append(-1)
                count.append(0)
                if direction:
                    right[node] = child
                else:
                    left[node] = child
            node = child
            count[node] += amount

    insert = add

    def count_value(self, value):
        value ^= self.lazy
        node = 0
        for bit in range(self.bit_length - 1, -1, -1):
            node = self.right[node] if value >> bit & 1 else self.left[node]
            if node < 0:
                return 0
        return self.count[node]

    count_of = count_value

    def discard(self, value, amount=1):
        current = self.count_value(value)
        amount = min(amount, current)
        if amount <= 0:
            return 0
        physical = value ^ self.lazy
        node = 0
        self.count[node] -= amount
        for bit in range(self.bit_length - 1, -1, -1):
            node = self.right[node] if physical >> bit & 1 else self.left[node]
            self.count[node] -= amount
        return amount

    erase = discard

    def xor_all(self, value):
        self.lazy ^= value

    apply_xor = xor_all

    def kth(self, index):
        if index < 0 or index >= self.count[0]:
            raise IndexError("kth index out of range")
        node = 0
        value = 0
        lazy = self.lazy
        for bit in range(self.bit_length - 1, -1, -1):
            lazy_bit = lazy >> bit & 1
            zero = self.right[node] if lazy_bit else self.left[node]
            zero_count = self.count[zero] if zero >= 0 else 0
            if index < zero_count:
                node = zero
            else:
                index -= zero_count
                node = self.left[node] if lazy_bit else self.right[node]
                value |= 1 << bit
        return value

    def min(self):
        return self.kth(0)

    def max(self):
        return self.kth(self.count[0] - 1)

    def bisect_left(self, value):
        node = 0
        result = 0
        lazy = self.lazy
        for bit in range(self.bit_length - 1, -1, -1):
            if node < 0:
                break
            lazy_bit = lazy >> bit & 1
            zero = self.right[node] if lazy_bit else self.left[node]
            one = self.left[node] if lazy_bit else self.right[node]
            if value >> bit & 1:
                if zero >= 0:
                    result += self.count[zero]
                node = one
            else:
                node = zero
        return result

    def xor_min(self, value):
        if not self.count[0]:
            raise IndexError("xor_min from empty BinaryTrie")
        node = 0
        stored = 0
        lazy = self.lazy
        for bit in range(self.bit_length - 1, -1, -1):
            desired = (lazy ^ value) >> bit & 1
            child = self.right[node] if desired else self.left[node]
            if child < 0 or self.count[child] == 0:
                desired ^= 1
                child = self.right[node] if desired else self.left[node]
            node = child
            stored |= (desired ^ (lazy >> bit & 1)) << bit
        return stored

    def xor_max(self, value):
        mask = (1 << self.bit_length) - 1
        return self.xor_min(value ^ mask)

    def __contains__(self, value):
        return self.count_value(value) > 0

    def __len__(self):
        return self.count[0]
