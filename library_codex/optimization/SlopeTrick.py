from heapq import heappop, heappush


class WeightedSlopeTrick:
    __slots__ = ("left", "right", "left_add", "right_add", "minimum")

    def __init__(self, constant=0):
        self.left = []
        self.right = []
        self.left_add = 0
        self.right_add = 0
        self.minimum = constant

    def _push_left(self, point, count):
        if count:
            heappush(self.left, (self.left_add - point, count))

    def _push_right(self, point, count):
        if count:
            heappush(self.right, (point - self.right_add, count))

    def _pop_left(self):
        point, count = heappop(self.left)
        return self.left_add - point, count

    def _pop_right(self):
        point, count = heappop(self.right)
        return point + self.right_add, count

    def get_min(self):
        if self.left:
            point = self.left_add - self.left[0][0]
        elif self.right:
            point = self.right[0][0] + self.right_add
        else:
            point = 0
        return point, self.minimum

    def add_constant(self, value):
        self.minimum += value

    shift_y = add_constant
    add_all = add_constant

    def add_x_minus_a(self, point, count=1):
        if count < 0:
            raise ValueError("count must be nonnegative")
        used = 0
        while used < count and self.left:
            current, current_count = self._pop_left()
            if current <= point:
                self._push_left(current, current_count)
                break
            moved = min(count - used, current_count)
            self._push_right(current, moved)
            self._push_left(current, current_count - moved)
            self.minimum += (current - point) * moved
            used += moved
        self._push_left(point, used)
        self._push_right(point, count - used)

    add_xma = add_x_minus_a

    def add_a_minus_x(self, point, count=1):
        if count < 0:
            raise ValueError("count must be nonnegative")
        used = 0
        while used < count and self.right:
            current, current_count = self._pop_right()
            if current >= point:
                self._push_right(current, current_count)
                break
            moved = min(count - used, current_count)
            self._push_left(current, moved)
            self._push_right(current, current_count - moved)
            self.minimum += (point - current) * moved
            used += moved
        self._push_right(point, used)
        self._push_left(point, count - used)

    add_amx = add_a_minus_x

    def add_abs(self, point, count=1):
        self.add_x_minus_a(point, count)
        self.add_a_minus_x(point, count)

    add_abs_xma = add_abs

    def shift_left(self, amount):
        self.left_add += amount

    shift_L = shift_left

    def shift_right(self, amount):
        self.right_add += amount

    shift_R = shift_right

    def shift(self, amount):
        self.left_add += amount
        self.right_add += amount

    shift_x = shift

    def slide(self, left, right):
        if left > right:
            raise ValueError("left must not exceed right")
        self.left_add += left
        self.right_add += right

    def chmin_right(self):
        self.right.clear()

    cum_min = chmin_right

    def chmin_left(self):
        self.left.clear()

    cum_min_right = chmin_left

    def evaluate(self, point):
        result = self.minimum
        left_add = self.left_add
        for stored, count in self.left:
            breakpoint = left_add - stored
            if breakpoint > point:
                result += (breakpoint - point) * count
        right_add = self.right_add
        for stored, count in self.right:
            breakpoint = stored + right_add
            if breakpoint < point:
                result += (point - breakpoint) * count
        return result

    eval = evaluate
    get_value = evaluate

    def merge(self, other):
        if len(self.left) + len(self.right) < len(other.left) + len(other.right):
            (
                self.left,
                other.left,
                self.right,
                other.right,
                self.left_add,
                other.left_add,
                self.right_add,
                other.right_add,
                self.minimum,
                other.minimum,
            ) = (
                other.left,
                self.left,
                other.right,
                self.right,
                other.left_add,
                self.left_add,
                other.right_add,
                self.right_add,
                other.minimum,
                self.minimum,
            )
        for stored, count in other.left:
            self.add_a_minus_x(other.left_add - stored, count)
        for stored, count in other.right:
            self.add_x_minus_a(stored + other.right_add, count)
        self.minimum += other.minimum
        other.clear()
        return self

    def clear(self):
        self.left.clear()
        self.right.clear()
        self.left_add = 0
        self.right_add = 0
        self.minimum = 0


SlopeTrick = WeightedSlopeTrick
