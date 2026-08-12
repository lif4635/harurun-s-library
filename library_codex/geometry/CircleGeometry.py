"""Intersections and tangent points involving circles."""

from math import hypot, sqrt


def circle_line_intersections(center, radius, line_start, line_end, eps=1e-12):
    """Return intersections of a circle and an infinite line."""
    if radius < 0:
        raise ValueError("radius must be nonnegative")
    cx, cy = center
    ax, ay = line_start
    dx = line_end[0] - ax
    dy = line_end[1] - ay
    norm = dx * dx + dy * dy
    if norm == 0:
        raise ValueError("a line requires two distinct points")
    scale = ((cx - ax) * dx + (cy - ay) * dy) / norm
    px = ax + scale * dx
    py = ay + scale * dy
    height2 = radius * radius - ((px - cx) ** 2 + (py - cy) ** 2)
    if height2 < -eps:
        return []
    if height2 <= eps:
        return [(px, py)]
    offset = sqrt(height2 / norm)
    return [(px - offset * dx, py - offset * dy), (px + offset * dx, py + offset * dy)]


def circle_circle_intersections(first_center, first_radius, second_center, second_radius, eps=1e-12):
    """Return circle intersections; ``None`` means coincident circles."""
    if first_radius < 0 or second_radius < 0:
        raise ValueError("radius must be nonnegative")
    dx = second_center[0] - first_center[0]
    dy = second_center[1] - first_center[1]
    distance = hypot(dx, dy)
    if distance <= eps:
        return None if abs(first_radius - second_radius) <= eps else []
    if distance > first_radius + second_radius + eps:
        return []
    if distance < abs(first_radius - second_radius) - eps:
        return []
    along = (first_radius ** 2 - second_radius ** 2 + distance ** 2) / (2 * distance)
    height2 = first_radius ** 2 - along ** 2
    px = first_center[0] + along * dx / distance
    py = first_center[1] + along * dy / distance
    if height2 <= eps:
        return [(px, py)]
    offset = sqrt(height2) / distance
    return [(px - offset * dy, py + offset * dx), (px + offset * dy, py - offset * dx)]


def tangent_points(center, radius, point, eps=1e-12):
    """Return points on the circle where tangents from ``point`` touch."""
    if radius < 0:
        raise ValueError("radius must be nonnegative")
    dx = point[0] - center[0]
    dy = point[1] - center[1]
    distance2 = dx * dx + dy * dy
    radius2 = radius * radius
    if distance2 < radius2 - eps:
        return []
    if distance2 <= radius2 + eps:
        return [tuple(point)]
    scale = radius2 / distance2
    offset = radius * sqrt(distance2 - radius2) / distance2
    px = center[0] + scale * dx
    py = center[1] + scale * dy
    return [(px - offset * dy, py + offset * dx), (px + offset * dy, py - offset * dx)]
