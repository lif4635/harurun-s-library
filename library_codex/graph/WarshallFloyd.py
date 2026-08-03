"""全頂点対最短距離を計算する。"""

INF = float("inf")

def warshall_floyd(matrix):
    distance = [list(row) for row in matrix]
    n = len(distance)
    for middle in range(n):
        middle_row = distance[middle]
        for first in range(n):
            base = distance[first][middle]
            if base == INF:
                continue
            row = distance[first]
            for second in range(n):
                value = base + middle_row[second]
                if value < row[second]:
                    row[second] = value
    return distance

