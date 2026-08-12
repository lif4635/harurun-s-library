"""Logarithmic point containment for a static convex polygon."""

from library_codex.geometry.Orientation import cross


def _on_segment(first, second, point):
    return (
        cross(first, second, point) == 0
        and min(first[0], second[0]) <= point[0] <= max(first[0], second[0])
        and min(first[1], second[1]) <= point[1] <= max(first[1], second[1])
    )


class ConvexPolygon:
    """Store a counterclockwise convex polygon for O(log N) containment."""

    __slots__ = ("points", "n")

    def __init__(self, polygon, validate=True):
        points = list(polygon)
        if len(points) > 1 and points[0] == points[-1]:
            points.pop()
        if len(points) >= 3:
            area = sum(
                points[index][0] * points[(index + 1) % len(points)][1]
                - points[index][1] * points[(index + 1) % len(points)][0]
                for index in range(len(points))
            )
            if area < 0:
                points.reverse()
            if validate:
                signs = [
                    cross(points[index - 1], points[index], points[(index + 1) % len(points)])
                    for index in range(len(points))
                ]
                if any(value < 0 for value in signs) or not any(value > 0 for value in signs):
                    raise ValueError("polygon must be convex with nonzero area")
        self.points = points
        self.n = len(points)

    def location(self, point):
        """Return 1 inside, 0 on the boundary, and -1 outside."""
        points = self.points
        n = self.n
        if n == 0:
            return -1
        if n == 1:
            return 0 if point == points[0] else -1
        if n == 2:
            return 0 if _on_segment(points[0], points[1], point) else -1
        first_side = cross(points[0], points[1], point)
        last_side = cross(points[0], points[-1], point)
        if first_side < 0 or last_side > 0:
            return -1
        if first_side == 0:
            return 0 if _on_segment(points[0], points[1], point) else -1
        if last_side == 0:
            return 0 if _on_segment(points[0], points[-1], point) else -1
        lower = 1
        upper = n - 1
        while upper - lower > 1:
            middle = (lower + upper) >> 1
            if cross(points[0], points[middle], point) >= 0:
                lower = middle
            else:
                upper = middle
        side = cross(points[lower], points[upper], point)
        return 1 if side > 0 else 0 if side == 0 else -1

    def contains(self, point, boundary=True):
        """Return whether the point is inside, optionally including boundary."""
        location = self.location(point)
        return location >= 0 if boundary else location > 0

    __contains__ = contains
