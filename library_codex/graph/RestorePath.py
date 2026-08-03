"""直前頂点列から始点から終点までのpathを復元する。"""

def restore_path(previous, goal, start=None):
    path = []
    node = goal
    while node >= 0:
        path.append(node)
        if node == start:
            break
        node = previous[node]
    if start is not None and path[-1] != start:
        return []
    path.reverse()
    return path

