from library_codex.math.Structures import SternBrocotNode


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
