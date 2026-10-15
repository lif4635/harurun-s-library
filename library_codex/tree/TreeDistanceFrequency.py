"""重みなし木について、距離ごとの順序を区別しない頂点対の個数を求める。"""

from library_codex.convolution.NTT import convolution_int, convolution_ntt
from library_codex.convolution.NTT998 import MOD, square


def _histogram_square(histogram):
    if len(histogram) <= 60 or len(histogram) > 1 << 22:
        return convolution_int(histogram, histogram)
    bound = max(histogram) * sum(histogram)
    second_mod = 469762049
    if bound >= MOD * second_mod:
        return convolution_int(histogram, histogram)
    result = square(histogram)
    if bound < MOD:
        return result
    other = convolution_ntt(histogram, histogram, second_mod)
    inverse = pow(MOD, -1, second_mod)
    for i in range(len(result)):
        result[i] += (other[i] - result[i]) * inverse % second_mod * MOD
    return result


def tree_distance_counts(tree, include_same=False):
    """距離dの頂点対数をresult[d]へ返す。時間 O(N log² N)、追加メモリ O(N)。"""
    n = len(tree)
    if n == 0:
        return []
    if sum(map(len, tree)) != 2 * (n - 1):
        raise ValueError("graph must be a tree")
    removed = bytearray(n)
    parent = [-2] * n
    sizes = [0] * n
    distances = [0] * n
    tasks = [0]
    answer = [0] * n
    first_component = True
    while tasks:
        start = tasks.pop()
        parent[start] = -1
        order = [start]
        sizes[start] = 1
        for vertex in order:
            for other in tree[vertex]:
                if removed[other] or other == parent[vertex]:
                    continue
                if first_component and parent[other] != -2:
                    raise ValueError("graph must be a tree")
                parent[other] = vertex
                sizes[other] = 1
                order.append(other)
        if first_component:
            if len(order) != n:
                raise ValueError("graph must be connected")
            first_component = False
        total_size = len(order)
        centroid = start
        for vertex in reversed(order):
            largest = total_size - sizes[vertex]
            for other in tree[vertex]:
                if not removed[other] and parent[other] == vertex:
                    largest = max(largest, sizes[other])
            if largest * 2 <= total_size:
                centroid = vertex
            if parent[vertex] >= 0:
                sizes[parent[vertex]] += sizes[vertex]
        removed[centroid] = 1
        if total_size == 1:
            continue
        total = [1]
        for neighbor in tree[centroid]:
            if removed[neighbor]:
                continue
            tasks.append(neighbor)
            parent[neighbor] = centroid
            distances[neighbor] = 1
            order = [neighbor]
            histogram = [0]
            for vertex in order:
                distance = distances[vertex]
                if distance == len(histogram):
                    histogram.append(1)
                else:
                    histogram[distance] += 1
                for other in tree[vertex]:
                    if not removed[other] and other != parent[vertex]:
                        parent[other] = vertex
                        distances[other] = distance + 1
                        order.append(other)
            if len(total) < len(histogram):
                total.extend([0] * (len(histogram) - len(total)))
            for distance in range(1, len(histogram)):
                total[distance] += histogram[distance]
            product = _histogram_square(histogram)
            for distance in range(1, min(n, len(product))):
                answer[distance] -= product[distance]
        product = _histogram_square(total)
        for distance in range(1, min(n, len(product))):
            answer[distance] += product[distance]
    for distance in range(1, n):
        answer[distance] >>= 1
    answer[0] = n if include_same else 0
    while len(answer) > 1 and answer[-1] == 0:
        answer.pop()
    return answer
