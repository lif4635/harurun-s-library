import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT.parent))

from library_codex.graph.GridBFS import grid_bfs, grid_shortest_path  # noqa: E402


def test_grid_bfs_distance_matrix_and_goal():
    grid = [
        "...#.",
        ".#.#.",
        ".#...",
        "...#.",
    ]
    distance = grid_bfs(grid, (0, 0))
    assert distance[0][0] == 0
    assert distance[3][2] == 5
    assert distance[0][3] == -1
    assert grid_shortest_path(grid, (0, 0), (2, 4)) == 6
    assert grid_shortest_path(grid, (0, 0), (0, 3)) == -1
    assert grid_bfs([".#", ".."], (0, 1)) == [[-1, -1], [-1, -1]]


def test_grid_bfs_custom_moves_and_block_value():
    grid = [[0, 1, 0], [0, 0, 0], [1, 0, 0]]
    moves = ((1, 1), (1, -1), (-1, 1), (-1, -1))
    distance = grid_bfs(grid, (0, 0), moves=moves, blocked=1)
    assert distance[2][2] == 2
    assert distance[1][1] == 1
