"""列の各位置について、その要素だけを除いた積をまとめて求める。"""


def all_but_one(values, op, identity):
    """result[i]をvalues[i]だけ除いた、元の順序での積として返す。"""
    values = list(values)
    n = len(values)
    result = [identity] * n
    product = identity
    for index, value in enumerate(values):
        result[index] = product
        product = op(product, value)
    product = identity
    for index in range(n - 1, -1, -1):
        result[index] = op(result[index], product)
        product = op(values[index], product)
    return result
