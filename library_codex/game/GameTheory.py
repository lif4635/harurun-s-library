class SurrealNumber:
    """A short surreal number represented as numerator / 2**exponent."""

    __slots__ = ("numerator", "exponent")

    def __init__(self, numerator=0, exponent=0):
        if exponent < 0:
            raise ValueError("exponent must be nonnegative")
        while numerator and exponent and numerator & 1 == 0:
            numerator >>= 1
            exponent -= 1
        if numerator == 0:
            exponent = 0
        self.numerator = numerator
        self.exponent = exponent

    @property
    def p(self):
        return self.numerator

    @property
    def q(self):
        return self.exponent

    def _coerce(self, other):
        return other if isinstance(other, SurrealNumber) else SurrealNumber(other)

    def __add__(self, other):
        other = self._coerce(other)
        exponent = max(self.exponent, other.exponent)
        numerator = ((self.numerator << (exponent - self.exponent))
                     + (other.numerator << (exponent - other.exponent)))
        return SurrealNumber(numerator, exponent)

    def __sub__(self, other):
        return self + -self._coerce(other)

    def __neg__(self):
        return SurrealNumber(-self.numerator, self.exponent)

    def _difference(self, other):
        return (self - self._coerce(other)).numerator

    def __lt__(self, other):
        return self._difference(other) < 0

    def __le__(self, other):
        return self._difference(other) <= 0

    def __gt__(self, other):
        return self._difference(other) > 0

    def __ge__(self, other):
        return self._difference(other) >= 0

    def __eq__(self, other):
        try:
            return self._difference(other) == 0
        except (TypeError, ValueError):
            return False

    def __hash__(self):
        return hash((self.numerator, self.exponent))

    def __repr__(self):
        if self.exponent == 0:
            return f"SurrealNumber({self.numerator})"
        return f"SurrealNumber({self.numerator}, {self.exponent})"

    def children(self):
        if self.numerator == 0:
            return SurrealNumber(-1), SurrealNumber(1)
        if self.exponent == 0 and self.numerator > 0:
            return (SurrealNumber(self.numerator * 2 - 1, 1),
                    SurrealNumber(self.numerator + 1))
        if self.exponent == 0:
            return (SurrealNumber(self.numerator - 1),
                    SurrealNumber(self.numerator * 2 + 1, 1))
        difference = SurrealNumber(1, self.exponent + 1)
        return self - difference, self + difference

    child = children

    def larger(self):
        result = SurrealNumber()
        while self >= result:
            result = result.children()[1]
        return result

    def smaller(self):
        result = SurrealNumber()
        while self <= result:
            result = result.children()[0]
        return result

    @staticmethod
    def between(left, right):
        left = left if isinstance(left, SurrealNumber) else SurrealNumber(left)
        right = right if isinstance(right, SurrealNumber) else SurrealNumber(right)
        if not left < right:
            raise ValueError("left must be smaller than right")
        result = SurrealNumber()
        while left >= result or result >= right:
            lower, upper = result.children()
            result = lower if right <= result else upper
        return result


def reduce_surreal(left, right):
    return SurrealNumber.between(left, right)


class ImpartialGameSolver:
    """Iterative Grundy solver for a DAG of hashable board states."""

    __slots__ = ("options", "splittable", "with_moves", "memo", "transitions")

    def __init__(self, options, splittable=False, with_moves=False):
        self.options = options
        self.splittable = splittable
        self.with_moves = with_moves
        self.memo = {}
        self.transitions = {}

    def _game_and_move(self, transition):
        if self.with_moves:
            return transition[0], transition[1]
        return transition, None

    def _boards(self, game):
        return tuple(game) if self.splittable else (game,)

    def get(self, board):
        if board in self.memo:
            return self.memo[board]
        stack = [(board, 0)]
        active = set()
        while stack:
            current, phase = stack.pop()
            if current in self.memo:
                continue
            if phase == 0:
                if current in active:
                    raise ValueError("game graph must be acyclic")
                active.add(current)
                transitions = list(self.options(current))
                self.transitions[current] = transitions
                stack.append((current, 1))
                dependencies = []
                for transition in transitions:
                    game, _ = self._game_and_move(transition)
                    dependencies.extend(self._boards(game))
                for dependency in reversed(dependencies):
                    if dependency not in self.memo:
                        stack.append((dependency, 0))
            else:
                reachable = set()
                for transition in self.transitions[current]:
                    game, _ = self._game_and_move(transition)
                    value = 0
                    for dependency in self._boards(game):
                        value ^= self.memo[dependency]
                    reachable.add(value)
                grundy = 0
                while grundy in reachable:
                    grundy += 1
                self.memo[current] = grundy
                active.remove(current)
        return self.memo[board]

    grundy = get

    def get_sum(self, boards):
        result = 0
        for board in boards:
            result ^= self.get(board)
        return result

    def get_best_move(self, game):
        if not self.with_moves:
            raise ValueError("with_moves=True is required")
        if self.splittable:
            total = self.get_sum(game)
            if total == 0:
                return None
            for index, board in enumerate(game):
                current = self.get(board)
                for transition in self.options(board):
                    next_game, move = self._game_and_move(transition)
                    next_value = self.get_sum(self._boards(next_game))
                    if total ^ current ^ next_value == 0:
                        return index, move
            return None
        if self.get(game) == 0:
            return None
        for transition in self.options(game):
            next_game, move = self._game_and_move(transition)
            next_value = 0
            for board in self._boards(next_game):
                next_value ^= self.get(board)
            if next_value == 0:
                return move
        return None


class PartisanGameSolver:
    """Iterative solver for short numeric partisan games."""

    __slots__ = ("options", "memo", "transitions")

    def __init__(self, options):
        self.options = options
        self.memo = {}
        self.transitions = {}

    def get(self, game):
        if game in self.memo:
            return self.memo[game]
        stack = [(game, 0)]
        active = set()
        while stack:
            current, phase = stack.pop()
            if current in self.memo:
                continue
            if phase == 0:
                if current in active:
                    raise ValueError("game graph must be acyclic")
                active.add(current)
                left, right = self.options(current)
                left, right = list(left), list(right)
                self.transitions[current] = left, right
                stack.append((current, 1))
                for child in reversed(left + right):
                    if child not in self.memo:
                        stack.append((child, 0))
            else:
                left, right = self.transitions[current]
                if not left and not right:
                    value = SurrealNumber()
                elif not right:
                    value = max(self.memo[child] for child in left).larger()
                elif not left:
                    value = min(self.memo[child] for child in right).smaller()
                else:
                    lower = max(self.memo[child] for child in left)
                    upper = min(self.memo[child] for child in right)
                    value = SurrealNumber.between(lower, upper)
                self.memo[current] = value
                active.remove(current)
        return self.memo[game]


Surreal = SurrealNumber
