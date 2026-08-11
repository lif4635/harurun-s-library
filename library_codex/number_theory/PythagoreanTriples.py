"""斜辺上限までのPythagorean tripleを重複なく列挙する。"""


def pythagorean_triples(limit, primitive_only=False):
    """a < bかつa^2+b^2=c^2、c<=limitのtupleを生成する。"""
    if limit < 0:
        raise ValueError("limit must be nonnegative")
    stack = [(3, 4, 5)] if limit >= 5 else []
    while stack:
        first, second, hypotenuse = stack.pop()
        children = (
            (first - 2 * second + 2 * hypotenuse,
             2 * first - second + 2 * hypotenuse,
             2 * first - 2 * second + 3 * hypotenuse),
            (first + 2 * second + 2 * hypotenuse,
             2 * first + second + 2 * hypotenuse,
             2 * first + 2 * second + 3 * hypotenuse),
            (-first + 2 * second + 2 * hypotenuse,
             -2 * first + second + 2 * hypotenuse,
             -2 * first + 2 * second + 3 * hypotenuse),
        )
        for child in children:
            if child[2] <= limit:
                stack.append(child)
        first, second = sorted((first, second))
        if primitive_only:
            yield first, second, hypotenuse
        else:
            multiple = 1
            while multiple * hypotenuse <= limit:
                yield multiple * first, multiple * second, multiple * hypotenuse
                multiple += 1
