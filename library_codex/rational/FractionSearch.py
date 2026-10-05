"""分子・分母の上限内で、数値や単調な判定条件を挟む既約分数を求める。"""

from library_codex.rational.SternBrocotNode import SternBrocotNode


def rational_bounds(numerator, denominator, limit):
    """分子・分母がlimit以下の分数で、正の有理数を上下から挟む。"""
    if numerator <= 0 or denominator <= 0 or limit < 1:
        raise ValueError("requires a positive fraction and limit >= 1")
    a, b, c, d = 0, 1, 1, 0
    lower_error, upper_error = numerator, denominator
    while a + c <= limit and b + d <= limit:
        if lower_error == upper_error:
            exact = a + c, b + d
            return exact, exact
        if lower_error > upper_error:
            steps = (lower_error - 1) // upper_error
            if c:
                steps = min(steps, (limit - a) // c)
            if d:
                steps = min(steps, (limit - b) // d)
            a += steps * c
            b += steps * d
            lower_error -= steps * upper_error
        else:
            steps = (upper_error - 1) // lower_error
            if a:
                steps = min(steps, (limit - c) // a)
            if b:
                steps = min(steps, (limit - d) // b)
            c += steps * a
            d += steps * b
            upper_error -= steps * lower_error
    return (a, b), (c, d)


def stern_brocot_binary_search(predicate, limit):
    """Bracket a monotone predicate among reduced nonnegative fractions."""
    if limit < 0:
        raise ValueError("limit must be nonnegative")
    node = SternBrocotNode()
    if limit == 0:
        return node.lower_bound(), node.upper_bound()
    if predicate((0, 1)):
        return (0, 1), (0, 1)

    def over(return_value):
        return (max(node.x, node.y) > limit
                or bool(predicate(node.get())) == return_value)

    go_left = over(True)
    while True:
        if go_left:
            amount = 1
            while True:
                node.go_left(amount)
                if over(False):
                    node.go_parent(amount)
                    break
                amount <<= 1
            amount >>= 1
            while amount:
                node.go_left(amount)
                if over(False):
                    node.go_parent(amount)
                amount >>= 1
            node.go_left(1)
            if max(node.x, node.y) > limit:
                return node.lower_bound(), node.upper_bound()
        else:
            amount = 1
            while True:
                node.go_right(amount)
                if over(True):
                    node.go_parent(amount)
                    break
                amount <<= 1
            amount >>= 1
            while amount:
                node.go_right(amount)
                if over(True):
                    node.go_parent(amount)
                amount >>= 1
            node.go_right(1)
            if max(node.x, node.y) > limit:
                return node.lower_bound(), node.upper_bound()
        go_left = not go_left


binary_search_on_stern_brocot_tree = stern_brocot_binary_search
