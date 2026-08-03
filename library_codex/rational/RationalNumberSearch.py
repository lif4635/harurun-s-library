"""条件を満たす有理数をStern-Brocot木上で探索する。"""

class RationalNumberSearch:
    """Adaptive Stern--Brocot search with numerator/denominator bounds."""

    __slots__ = ("maximum", "a0", "b0", "a1", "b1", "left", "right", "state")

    def __init__(self, maximum):
        if maximum <= 0:
            raise ValueError("maximum must be positive")
        self.maximum = maximum
        self.a0, self.b0 = 0, 1
        self.a1, self.b1 = 1, 0
        self.left = self.right = 0
        self.state = 0

    def has_next(self):
        return self.state >= 0

    def get_next(self):
        state = self.state
        if state == 0:
            return self.a0 + self.a1, self.b0 + self.b1
        middle = (self.left + self.right) >> 1
        if state == 1:
            return self.a0 + self.right * self.a1, self.b0 + self.right * self.b1
        if state == 2:
            return self.a1 + self.right * self.a0, self.b1 + self.right * self.b0
        if state == 3:
            return self.a0 + middle * self.a1, self.b0 + middle * self.b1
        if state == 4:
            return self.a1 + middle * self.a0, self.b1 + middle * self.b0
        raise StopIteration

    def give(self, to_right):
        direction = 1 if to_right else 0
        state = self.state
        if state == 0:
            self.left, self.right = 1, 2
            if self.a0 + self.a1 > self.maximum or self.b0 + self.b1 > self.maximum:
                self.state = -1
            else:
                self.state = 1 if to_right else 2
        elif state in (1, 2):
            if direction ^ (2 - state):
                self.state += 2
            else:
                self.left <<= 1
                self.right <<= 1
        elif state in (3, 4):
            if direction ^ (4 - state):
                self.right = (self.left + self.right) >> 1
            else:
                self.left = (self.left + self.right) >> 1
        while self._normalize():
            pass

    def _normalize(self):
        state = self.state
        if state < 0:
            return False
        if state == 0:
            if self.a0 + self.a1 > self.maximum or self.b0 + self.b1 > self.maximum:
                self.state = -1
            return False
        if state in (1, 2):
            changed = False
            if state == 1:
                pairs = ((self.a0, self.a1), (self.b0, self.b1))
            else:
                pairs = ((self.a1, self.a0), (self.b1, self.b0))
            for base, step in pairs:
                if base + self.right * step > self.maximum:
                    self.right = (self.maximum - base) // step + 1
                    changed = True
            if changed:
                self.state += 2
                return True
            return False
        if self.left + 1 != self.right:
            return False
        if state == 3:
            self.a0 += self.a1 * self.left
            self.b0 += self.b1 * self.left
            self.a1 += self.a0
            self.b1 += self.b0
        else:
            self.a1 += self.a0 * self.left
            self.b1 += self.b0 * self.left
            self.a0 += self.a1
            self.b0 += self.b1
        self.state = 0
        return True

