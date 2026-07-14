class FastSet:
    __slots__ = ("n", "level", "size")

    def __init__(self, size, values=()):
        if size < 0:
            raise ValueError("size must be nonnegative")
        level = []
        length = size
        while True:
            level.append([0] * ((length + 63) >> 6))
            if length <= 64:
                break
            length = (length + 63) >> 6
        self.n = size
        self.level = level
        self.size = 0
        for value in values:
            self.add(value)

    def add(self, value):
        if not 0 <= value < self.n:
            raise IndexError("value is out of range")
        level = self.level
        index = value
        word_index = index >> 6
        mask = 1 << (index & 63)
        if level[0][word_index] & mask:
            return False
        self.size += 1
        for words in level:
            word_index = index >> 6
            mask = 1 << (index & 63)
            old = words[word_index]
            words[word_index] = old | mask
            if old:
                break
            index = word_index
        return True

    insert = add

    def discard(self, value):
        if not 0 <= value < self.n:
            return False
        level = self.level
        index = value
        word_index = index >> 6
        mask = 1 << (index & 63)
        if not level[0][word_index] & mask:
            return False
        self.size -= 1
        for words in level:
            word_index = index >> 6
            words[word_index] &= ~(1 << (index & 63))
            if words[word_index]:
                break
            index = word_index
        return True

    erase = discard

    def next(self, value):
        if value < 0:
            value = 0
        if value >= self.n:
            return -1
        index = value
        found_level = -1
        for height, words in enumerate(self.level):
            word_index = index >> 6
            if word_index >= len(words):
                return -1
            shifted = words[word_index] >> (index & 63)
            if shifted:
                index += (shifted & -shifted).bit_length() - 1
                found_level = height
                break
            index = word_index + 1
        if found_level < 0:
            return -1
        for height in range(found_level - 1, -1, -1):
            index <<= 6
            word = self.level[height][index >> 6]
            index += (word & -word).bit_length() - 1
        return index if index < self.n else -1

    ge = next

    def prev(self, value):
        if value >= self.n:
            value = self.n - 1
        if value < 0:
            return -1
        index = value
        found_level = -1
        for height, words in enumerate(self.level):
            word_index = index >> 6
            mask = words[word_index] & ((1 << ((index & 63) + 1)) - 1)
            if mask:
                index = (word_index << 6) + mask.bit_length() - 1
                found_level = height
                break
            if word_index == 0:
                return -1
            index = word_index - 1
        if found_level < 0:
            return -1
        for height in range(found_level - 1, -1, -1):
            index = (index << 6) | 63
            words = self.level[height]
            word_index = index >> 6
            if word_index >= len(words):
                word_index = len(words) - 1
            word = words[word_index]
            index = (word_index << 6) + word.bit_length() - 1
        return index

    le = prev

    def min(self):
        value = self.next(0)
        if value < 0:
            raise ValueError("min of empty FastSet")
        return value

    def max(self):
        value = self.prev(self.n - 1)
        if value < 0:
            raise ValueError("max of empty FastSet")
        return value

    def __contains__(self, value):
        return (
            0 <= value < self.n
            and bool(self.level[0][value >> 6] >> (value & 63) & 1)
        )

    def __len__(self):
        return self.size
