"""複数の集合対について、共通要素数をまとめて求める。"""

from math import isqrt


def intersection_sizes(sets, queries):
    """各(i, j)についてsets[i]とsets[j]の共通要素数を返す。"""
    rows = [set(row) for row in sets]
    pairs = list(queries)
    n = len(rows)
    for first, second in pairs:
        if not 0 <= first < n or not 0 <= second < n:
            raise IndexError("a query set index is outside the input")
    if not pairs:
        return []

    unique = []
    query_id = {}
    ids = []
    for first, second in pairs:
        if first > second:
            first, second = second, first
        pair = (first, second)
        index = query_id.get(pair)
        if index is None:
            index = len(unique)
            query_id[pair] = index
            unique.append(pair)
        ids.append(index)

    active_vertices = sorted({vertex for pair in unique for vertex in pair})
    active_id = {vertex: index for index, vertex in enumerate(active_vertices)}
    element_id = {}
    encoded = []
    members = []
    for vertex in active_vertices:
        current = []
        for value in rows[vertex]:
            index = element_id.get(value)
            if index is None:
                index = len(members)
                element_id[value] = index
                members.append([])
            current.append(index)
            members[index].append(active_id[vertex])
        encoded.append(current)

    threshold = max(1, isqrt(len(unique)))
    heavy_id = [-1] * len(members)
    heavy_count = 0
    for element, containing in enumerate(members):
        if len(containing) >= threshold:
            heavy_id[element] = heavy_count
            heavy_count += 1

    heavy_mask = [0] * len(active_vertices)
    light = [[] for _ in active_vertices]
    for vertex, elements in enumerate(encoded):
        mask = 0
        target = light[vertex]
        for element in elements:
            bit = heavy_id[element]
            if bit < 0:
                target.append(element)
            else:
                mask |= 1 << bit
        heavy_mask[vertex] = mask

    answer = [0] * len(unique)
    by_first = [[] for _ in active_vertices]
    for query, (first, second) in enumerate(unique):
        left = active_id[first]
        right = active_id[second]
        answer[query] = (heavy_mask[left] & heavy_mask[right]).bit_count()
        by_first[left].append((query, right))

    counts = [0] * len(active_vertices)
    touched = []
    for first, grouped in enumerate(by_first):
        if not grouped or not light[first]:
            continue
        for element in light[first]:
            for second in members[element]:
                if counts[second] == 0:
                    touched.append(second)
                counts[second] += 1
        for query, second in grouped:
            answer[query] += counts[second]
        for second in touched:
            counts[second] = 0
        touched.clear()
    return [answer[index] for index in ids]
