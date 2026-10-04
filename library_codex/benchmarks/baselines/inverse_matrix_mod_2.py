class F2Matrix:
    __slots__ = ('height', 'width', 'rows')

    def __init__(self, height, width=None, rows=None):
        if width is None:
            width = height
        if height < 0 or width < 0:
            raise ValueError('matrix dimensions must be nonnegative')
        self.height = height
        self.width = width
        mask = (1 << width) - 1
        if rows is None:
            self.rows = [0] * height
        else:
            if len(rows) != height:
                raise ValueError('invalid row count')
            self.rows = [row & mask for row in rows]

    @classmethod
    def from_lists(cls, matrix):
        height = len(matrix)
        width = len(matrix[0]) if height else 0
        rows = [0] * height
        for (row, values) in enumerate(matrix):
            if len(values) != width:
                raise ValueError('matrix rows must have equal length')
            bits = 0
            for (column, value) in enumerate(values):
                bits |= (value & 1) << column
            rows[row] = bits
        return cls(height, width, rows)

    @classmethod
    def identity(cls, size):
        return cls(size, size, [1 << index for index in range(size)])

    def copy(self):
        return F2Matrix(self.height, self.width, self.rows)

    def to_lists(self):
        return [[bits >> column & 1 for column in range(self.width)] for bits in self.rows]

    def get(self, row, column):
        return self.rows[row] >> column & 1

    def set(self, row, column, value=True):
        bit = 1 << column
        if value:
            self.rows[row] |= bit
        else:
            self.rows[row] &= ~bit

    def multiply(self, other):
        if self.width != other.height:
            raise ValueError('incompatible matrix shapes')
        result = [0] * self.height
        source_rows = other.rows
        blocks = self.width + 7 >> 3
        if sum((row.bit_count() for row in self.rows)) > blocks * (self.height + 255):
            for start in range(0, self.width, 8):
                table = [0]
                for source in source_rows[start:start + 8]:
                    table += [value ^ source for value in table]
                mask = len(table) - 1
                for (row, bits) in enumerate(self.rows):
                    result[row] ^= table[bits >> start & mask]
            return F2Matrix(self.height, other.width, result)
        for (row, bits) in enumerate(self.rows):
            value = 0
            while bits:
                least = bits & -bits
                value ^= source_rows[least.bit_length() - 1]
                bits ^= least
            result[row] = value
        return F2Matrix(self.height, other.width, result)

    def and_or_product(self, other):
        if self.width != other.height:
            raise ValueError('incompatible matrix shapes')
        result = [0] * self.height
        source_rows = other.rows
        for (row, bits) in enumerate(self.rows):
            value = 0
            while bits:
                least = bits & -bits
                value |= source_rows[least.bit_length() - 1]
                bits ^= least
            result[row] = value
        return F2Matrix(self.height, other.width, result)

    def power(self, exponent):
        if self.height != self.width:
            raise ValueError('matrix must be square')
        if exponent < 0:
            raise ValueError('exponent must be nonnegative')
        result = F2Matrix.identity(self.height)
        base = self.copy()
        while exponent:
            if exponent & 1:
                result = result.multiply(base)
            exponent >>= 1
            if exponent:
                base = base.multiply(base)
        return result

    def sweep(self, pivot_end=None):
        if pivot_end is None:
            pivot_end = self.width
        if not 0 <= pivot_end <= self.width:
            raise ValueError('invalid pivot_end')
        rank = 0
        pivots = []
        rows = self.rows
        for column in range(pivot_end):
            bit = 1 << column
            pivot = rank
            while pivot < self.height and (not rows[pivot] & bit):
                pivot += 1
            if pivot == self.height:
                continue
            (rows[rank], rows[pivot]) = (rows[pivot], rows[rank])
            pivot_row = rows[rank]
            for row in range(self.height):
                if row != rank and rows[row] & bit:
                    rows[row] ^= pivot_row
            pivots.append(column)
            rank += 1
            if rank == self.height:
                break
        return (rank, pivots)

    def rank(self):
        rank = 0
        if self.width <= 2 * self.height:
            basis = [0] * self.width
            for value in self.rows:
                while value:
                    column = value.bit_length() - 1
                    pivot = basis[column]
                    if pivot:
                        value ^= pivot
                    else:
                        basis[column] = value
                        rank += 1
                        break
        else:
            basis = {}
            for value in self.rows:
                while value:
                    column = value.bit_length() - 1
                    pivot = basis.get(column)
                    if pivot:
                        value ^= pivot
                    else:
                        basis[column] = value
                        rank += 1
                        break
        return rank

    def determinant(self):
        if self.height != self.width:
            raise ValueError('matrix must be square')
        return int(self.rank() == self.height)

    def inverse(self):
        if self.height != self.width:
            raise ValueError('matrix must be square')
        size = self.height
        combined = F2Matrix(size, size * 2, [self.rows[row] | 1 << size + row for row in range(size)])
        (rank, _) = combined.sweep(size)
        if rank != size:
            return None
        mask = (1 << size) - 1
        return F2Matrix(size, size, [row >> size & mask for row in combined.rows])

    def matvec(self, vector):
        if isinstance(vector, int):
            bits = vector
            return_integer = True
        else:
            if len(vector) != self.width:
                raise ValueError('invalid vector size')
            bits = 0
            for (column, value) in enumerate(vector):
                bits |= (value & 1) << column
            return_integer = False
        result = 0
        for (row, source) in enumerate(self.rows):
            result |= ((source & bits).bit_count() & 1) << row
        if return_integer:
            return result
        return [result >> row & 1 for row in range(self.height)]

    def __mul__(self, other):
        return self.multiply(other)

    def __pow__(self, exponent):
        return self.power(exponent)

    def __eq__(self, other):
        return isinstance(other, F2Matrix) and self.height == other.height and (self.width == other.width) and (self.rows == other.rows)
F2_Matrix = F2Matrix
and_or_product = F2Matrix.and_or_product
import sys

def main():
    read = sys.stdin.buffer.readline
    n = int(read())
    rows = [int(read().strip()[::-1], 2) for _ in range(n)]
    result = F2Matrix(n, n, rows).inverse()
    if result is None:
        print(-1)
    else:
        spec = '0' + str(n) + 'b'
        sys.stdout.write('\n'.join((format(row, spec)[::-1] for row in result.rows)) + '\n')
if __name__ == '__main__':
    main()
