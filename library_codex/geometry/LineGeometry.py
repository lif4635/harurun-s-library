"""Projection, reflection, distance, and intersection for infinite lines."""

from math import hypot


def projection(point, line_start, line_end):
    """Return the orthogonal projection of ``point`` onto an infinite line."""
    ax, ay = line_start
    dx = line_end[0] - ax
    dy = line_end[1] - ay
    norm = dx * dx + dy * dy
    if norm == 0:
        raise ValueError("a line requires two distinct points")
    scale = ((point[0] - ax) * dx + (point[1] - ay) * dy) / norm
    return ax + scale * dx, ay + scale * dy


def reflection(point, line_start, line_end):
    """Return the mirror image of ``point`` across an infinite line."""
    px, py = projection(point, line_start, line_end)
    return 2 * px - point[0], 2 * py - point[1]


def distance_to_line(point, line_start, line_end):
    """Return the Euclidean distance from a point to an infinite line."""
    px, py = projection(point, line_start, line_end)
    return hypot(point[0] - px, point[1] - py)


def line_intersection(first_start, first_end, second_start, second_end):
    """Return the unique intersection of two infinite lines, or ``None``."""
    ax, ay = first_start
    bx, by = first_end
    cx, cy = second_start
    dx, dy = second_end
    first_x, first_y = bx - ax, by - ay
    second_x, second_y = dx - cx, dy - cy
    determinant = first_x * second_y - first_y * second_x
    if determinant == 0:
        return None
    scale = ((cx - ax) * second_y - (cy - ay) * second_x) / determinant
    return ax + scale * first_x, ay + scale * first_y
