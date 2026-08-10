"""Fast reproducible randomness for generated test cases."""


_MASK64 = (1 << 64) - 1


class Random:
    """SplitMix64-seeded xoshiro256** generator with test-data helpers."""

    __slots__ = ("state",)

    def __init__(self, seed=0):
        state = []
        for _ in range(4):
            seed = (seed + 0x9E3779B97F4A7C15) & _MASK64
            value = seed
            value = ((value ^ (value >> 30)) * 0xBF58476D1CE4E5B9) & _MASK64
            value = ((value ^ (value >> 27)) * 0x94D049BB133111EB) & _MASK64
            state.append((value ^ (value >> 31)) & _MASK64)
        self.state = state

    @staticmethod
    def _rotate(value, shift):
        return ((value << shift) | (value >> (64 - shift))) & _MASK64

    def next_u64(self):
        """Return the next unsigned 64-bit integer."""
        state = self.state
        result = self._rotate(state[1] * 5 & _MASK64, 7) * 9 & _MASK64
        temporary = state[1] << 17 & _MASK64
        state[2] ^= state[0]
        state[3] ^= state[1]
        state[1] ^= state[2]
        state[0] ^= state[3]
        state[2] ^= temporary
        state[3] = self._rotate(state[3], 45)
        return result

    def randrange(self, lower, upper=None):
        """Return a uniform integer in the half-open interval [lower, upper)."""
        if upper is None:
            upper = lower
            lower = 0
        if lower >= upper:
            raise ValueError("empty random range")
        width = upper - lower
        limit = (1 << 64) - ((1 << 64) % width)
        while True:
            value = self.next_u64()
            if value < limit:
                return lower + value % width

    def uniform(self, lower, upper):
        """Return a uniform integer in the inclusive interval [lower, upper]."""
        return self.randrange(lower, upper + 1)

    def uniform_bool(self):
        """Return False or True with equal probability."""
        return bool(self.next_u64() & 1)

    def uniform01(self):
        """Return a uniform float in [0.0, 1.0) with 53 random bits."""
        return (self.next_u64() >> 11) * (1.0 / (1 << 53))

    def choice(self, values):
        """Return one uniformly selected element from a nonempty sequence."""
        if not values:
            raise IndexError("cannot choose from an empty sequence")
        return values[self.randrange(len(values))]

    def shuffle(self, values):
        """Shuffle a mutable sequence in place and return it."""
        for index in range(1, len(values)):
            target = self.randrange(index + 1)
            values[index], values[target] = values[target], values[index]
        return values

    def permutation(self, size, start=0):
        """Return a shuffled list containing start through start+size-1."""
        if size < 0:
            raise ValueError("size must be nonnegative")
        return self.shuffle(list(range(start, start + size)))

    def sample(self, values, count):
        """Return count distinct elements in random order without replacement."""
        if count < 0 or count > len(values):
            raise ValueError("invalid sample size")
        values = list(values)
        for index in range(count):
            target = self.randrange(index, len(values))
            values[index], values[target] = values[target], values[index]
        return values[:count]

    def sample_range(self, count, lower, upper, sort_result=True):
        """Sample distinct integers from the inclusive interval [lower, upper]."""
        population = upper - lower + 1
        if count < 0 or count > population:
            raise ValueError("invalid sample size")
        selected = set()
        for value in range(population - count, population):
            candidate = self.randrange(value + 1)
            selected.add(value if candidate in selected else candidate)
        result = [value + lower for value in selected]
        if sort_result:
            result.sort()
        else:
            self.shuffle(result)
        return result

    def array(self, length, lower, upper, distinct=False, sort_result=False):
        """Return a test array whose values are in inclusive [lower, upper]."""
        if length < 0:
            raise ValueError("length must be nonnegative")
        if lower > upper:
            raise ValueError("lower must not exceed upper")
        if distinct:
            return self.sample_range(length, lower, upper, sort_result)
        result = [self.uniform(lower, upper) for _ in range(length)]
        if sort_result:
            result.sort()
        return result

    def bits(self, length, ones=None):
        """Return a binary array, optionally with an exact number of ones."""
        if length < 0:
            raise ValueError("length must be nonnegative")
        if ones is None:
            return [self.next_u64() & 1 for _ in range(length)]
        if not 0 <= ones <= length:
            raise ValueError("ones must be between zero and length")
        result = [1] * ones + [0] * (length - ones)
        return self.shuffle(result)

    def matrix(self, rows, columns, lower, upper):
        """Return a rows-by-columns random integer matrix."""
        if rows < 0 or columns < 0:
            raise ValueError("matrix dimensions must be nonnegative")
        return [self.array(columns, lower, upper) for _ in range(rows)]

    def string(self, length, alphabet="abcdefghijklmnopqrstuvwxyz"):
        """Return a random string of the requested length from alphabet."""
        if length < 0:
            raise ValueError("length must be nonnegative")
        if not alphabet and length:
            raise ValueError("alphabet must be nonempty")
        return "".join(self.choice(alphabet) for _ in range(length))

    def intervals(self, count, lower, upper, allow_empty=False):
        """Return random half-open intervals contained in [lower, upper)."""
        if count < 0 or lower > upper:
            raise ValueError("invalid interval request")
        if not allow_empty and lower == upper and count:
            raise ValueError("a nonempty interval needs lower < upper")
        result = []
        for _ in range(count):
            if allow_empty:
                left = self.uniform(lower, upper)
                right = self.uniform(left, upper)
            else:
                left = self.randrange(lower, upper)
                right = self.randrange(left + 1, upper + 1)
            result.append((left, right))
        return result

    def composition(self, total, parts, positive=False):
        """Return a uniform ordered composition of total into parts integers."""
        minimum = parts if positive else 0
        if total < minimum or parts < 0 or (parts == 0 and total != 0):
            raise ValueError("no composition satisfies the request")
        if parts == 0:
            return []
        remaining = total - minimum
        bars = self.sample_range(parts - 1, 0, remaining + parts - 2)
        positions = [-1] + bars + [remaining + parts - 1]
        offset = 1 if positive else 0
        return [
            positions[index + 1] - positions[index] - 1 + offset
            for index in range(parts)
        ]

    def brackets(self, pairs, opening="(", closing=")"):
        """Return a uniformly random balanced bracket string with pairs pairs."""
        if pairs < 0:
            raise ValueError("pairs must be nonnegative")
        if not isinstance(opening, str) or not isinstance(closing, str):
            raise TypeError("opening and closing must be strings")
        steps = [1] * (pairs + 1) + [-1] * pairs
        self.shuffle(steps)
        balance = 0
        minimum = 0
        start = 0
        for index, step in enumerate(steps, 1):
            balance += step
            if balance <= minimum:
                minimum = balance
                start = index
        steps = steps[start:] + steps[:start]
        steps = steps[1:]
        return "".join(opening if step > 0 else closing for step in steps)

    def monge(self, rows, columns, difference_max=10, offset=10):
        """Return a random integer Monge matrix of shape rows by columns."""
        if rows < 0 or columns < 0:
            raise ValueError("matrix dimensions must be nonnegative")
        if difference_max < 0 or offset < 0:
            raise ValueError("difference_max and offset must be nonnegative")
        matrix = [[0] * columns for _ in range(rows)]
        for row in range(1, rows):
            previous = matrix[row - 1]
            current = matrix[row]
            for column in range(1, columns):
                current[column] = (
                    previous[column]
                    + current[column - 1]
                    - previous[column - 1]
                    - self.uniform(0, difference_max)
                )
        row_offset = [self.uniform(-offset, offset) for _ in range(rows)]
        column_offset = [
            self.uniform(-offset, offset) for _ in range(columns)
        ]
        for row in range(rows):
            current = matrix[row]
            addition = row_offset[row]
            for column in range(columns):
                current[column] += addition + column_offset[column]
        return matrix
