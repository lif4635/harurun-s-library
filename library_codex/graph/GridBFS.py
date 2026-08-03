"""障害物付きgrid上の最短距離をBFSで求める。"""

from collections import deque


DIR4 = ((1, 0), (-1, 0), (0, 1), (0, -1))


def grid_bfs(grid, start, moves=DIR4, blocked="#"):
    """startから各cellへの最短移動回数を、到達不能を-1として返す。O(HW)。"""
    height = len(grid)
    width = len(grid[0]) if height else 0
    if any(len(row) != width for row in grid):
        raise ValueError("grid must be rectangular")
    row, column = start
    if not 0 <= row < height or not 0 <= column < width:
        raise IndexError("start is outside the grid")
    distance = [[-1] * width for _ in range(height)]
    if grid[row][column] == blocked:
        return distance
    distance[row][column] = 0
    queue = deque(((row, column),))
    while queue:
        row, column = queue.popleft()
        next_distance = distance[row][column] + 1
        for delta_row, delta_column in moves:
            next_row = row + delta_row
            next_column = column + delta_column
            if (
                0 <= next_row < height
                and 0 <= next_column < width
                and distance[next_row][next_column] < 0
                and grid[next_row][next_column] != blocked
            ):
                distance[next_row][next_column] = next_distance
                queue.append((next_row, next_column))
    return distance


def grid_shortest_path(grid, start, goal, moves=DIR4, blocked="#"):
    """startからgoalへの最短移動回数を返し、到達不能なら-1を返す。O(HW)。"""
    row, column = goal
    distance = grid_bfs(grid, start, moves, blocked)
    if not 0 <= row < len(distance) or not distance or not 0 <= column < len(distance[0]):
        raise IndexError("goal is outside the grid")
    return distance[row][column]
