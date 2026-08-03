"""2次元点の外積と向きを整数演算で判定する。"""


def cross(origin, first, second):
    """ベクトル origin→first と origin→second の外積を返す。O(1)。"""
    return ((first[0] - origin[0]) * (second[1] - origin[1])
            - (first[1] - origin[1]) * (second[0] - origin[0]))


def orientation(first, second, third):
    """3点の向きを反時計回りなら1、時計回りなら-1、一直線なら0で返す。O(1)。"""
    value = cross(first, second, third)
    return (value > 0) - (value < 0)
