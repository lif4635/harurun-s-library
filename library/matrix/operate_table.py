def transpose_table(mat):
    """
    転置行列
    """
    return [list(x) for x in zip(*mat)]

def rotate_table(table):
    """
    反時計回りに回転
    """
    return list(map(list, zip(*table)))[::-1]
