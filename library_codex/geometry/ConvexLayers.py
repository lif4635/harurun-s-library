"""Onion decomposition of planar points."""

from library_codex.geometry.ConvexHull import convex_hull


def convex_layers(points, keep_collinear=True):
    """Peel convex hulls and return the point sequence of every layer.

    Equal coordinates are treated as one geometric point.  With
    ``keep_collinear=True``, every point on a layer boundary is removed at
    once.
    """
    remaining = set(points)
    layers = []
    while remaining:
        if len(remaining) <= 2:
            layer = sorted(remaining)
        else:
            layer = convex_hull(remaining, keep_collinear)
        layers.append(layer)
        remaining.difference_update(layer)
    return layers


def onion_depth(points, keep_collinear=True):
    """Return the zero-based convex layer number of each input point."""
    depth = {}
    for layer_id, layer in enumerate(convex_layers(points, keep_collinear)):
        for point in layer:
            depth[point] = layer_id
    return [depth[point] for point in points]
