"""bipartite multigraphの辺を最小色数で彩色する。"""


def bipartite_edge_coloring(left_size, right_size, edges):
    """同じ頂点に接する辺が異色になるよう、各辺の色番号を返す。"""
    edges = list(edges)
    if left_size < 0 or right_size < 0:
        raise ValueError("part sizes must be nonnegative")
    degree_left = [0] * left_size
    degree_right = [0] * right_size
    all_edges = []
    for edge_id, (left, right) in enumerate(edges):
        if not 0 <= left < left_size or not 0 <= right < right_size:
            raise IndexError("edge endpoint is out of range")
        degree_left[left] += 1
        degree_right[right] += 1
        all_edges.append((left, right, edge_id))
    colors = [-1] * len(edges)
    delta = max(degree_left + degree_right, default=0)
    if delta == 0:
        return colors

    size = max(left_size, right_size)
    degree_left += [0] * (size - left_size)
    degree_right += [0] * (size - right_size)
    left = right = 0
    need_left = [delta - value for value in degree_left]
    need_right = [delta - value for value in degree_right]
    while left < size and right < size:
        while left < size and need_left[left] == 0:
            left += 1
        while right < size and need_right[right] == 0:
            right += 1
        if left == size or right == size:
            break
        count = min(need_left[left], need_right[right])
        for _ in range(count):
            all_edges.append((left, right, -1))
        need_left[left] -= count
        need_right[right] -= count

    adjacency = [[] for _ in range(size)]
    for edge_id, (left, _, _) in enumerate(all_edges):
        adjacency[left].append(edge_id)
    active = bytearray(b"\1") * len(all_edges)

    for color in range(delta):
        match_left = [-1] * size
        match_right = [-1] * size
        match_edge_left = [-1] * size
        while True:
            distance = [-1] * size
            queue = []
            for vertex in range(size):
                if match_left[vertex] < 0:
                    distance[vertex] = 0
                    queue.append(vertex)
            reachable_free = False
            for vertex in queue:
                for edge_id in adjacency[vertex]:
                    if not active[edge_id]:
                        continue
                    right_vertex = all_edges[edge_id][1]
                    matched = match_right[right_vertex]
                    if matched < 0:
                        reachable_free = True
                    elif distance[matched] < 0:
                        distance[matched] = distance[vertex] + 1
                        queue.append(matched)
            if not reachable_free:
                break

            augmented = 0
            next_edge = [0] * size
            for root in range(size):
                if match_left[root] >= 0:
                    continue
                stack = [root]
                path = []
                found_edge = -1
                while stack:
                    vertex = stack[-1]
                    choices = adjacency[vertex]
                    advanced = False
                    while next_edge[vertex] < len(choices):
                        edge_id = choices[next_edge[vertex]]
                        next_edge[vertex] += 1
                        if not active[edge_id]:
                            continue
                        right_vertex = all_edges[edge_id][1]
                        matched = match_right[right_vertex]
                        if matched < 0:
                            found_edge = edge_id
                            break
                        if distance[matched] == distance[vertex] + 1:
                            path.append(edge_id)
                            stack.append(matched)
                            advanced = True
                            break
                    if found_edge >= 0:
                        break
                    if advanced:
                        continue
                    distance[vertex] = -1
                    stack.pop()
                    if path:
                        path.pop()
                if found_edge < 0:
                    continue
                assignments = path + [found_edge]
                for vertex, edge_id in zip(stack, assignments):
                    right_vertex = all_edges[edge_id][1]
                    match_left[vertex] = right_vertex
                    match_right[right_vertex] = vertex
                    match_edge_left[vertex] = edge_id
                augmented += 1
            if augmented == 0:
                break

        if any(edge_id < 0 for edge_id in match_edge_left):
            raise ArithmeticError("regular bipartite matching failed")
        for edge_id in match_edge_left:
            active[edge_id] = 0
            original = all_edges[edge_id][2]
            if original >= 0:
                colors[original] = color
    return colors
