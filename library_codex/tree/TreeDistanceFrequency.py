"""Frequency table of all unordered vertex-pair distances."""

from library_codex.convolution.NTT import convolution_int
from library_codex.tree.CentroidDecomposition import CentroidDecomposition


def frequency_table_of_tree_distance(tree, include_same=False):
    """Return counts indexed by unweighted distance.

    By default only unordered pairs of distinct vertices are counted.  With
    ``include_same=True``, index 0 is the number of vertices.  Centroid paths
    are built iteratively and all histogram products use exact integer CRT
    convolution.
    """
    n = len(tree)
    if n == 0:
        return []
    decomposition = CentroidDecomposition(tree)
    total = [[] for _ in range(n)]
    branch = {}
    for vertex in range(n):
        for centroid, distance, branch_id in decomposition.paths[vertex]:
            histogram = total[centroid]
            if len(histogram) <= distance:
                histogram.extend([0] * (distance + 1 - len(histogram)))
            histogram[distance] += 1
            if branch_id >= 0:
                key = (centroid, branch_id)
                histogram = branch.get(key)
                if histogram is None:
                    histogram = []
                    branch[key] = histogram
                if len(histogram) <= distance:
                    histogram.extend([0] * (distance + 1 - len(histogram)))
                histogram[distance] += 1
    answer = [0] * n
    for histogram in total:
        if not histogram:
            continue
        product = convolution_int(histogram, histogram)
        limit = min(n, len(product))
        for distance in range(limit):
            answer[distance] += product[distance]
    for histogram in branch.values():
        product = convolution_int(histogram, histogram)
        limit = min(n, len(product))
        for distance in range(limit):
            answer[distance] -= product[distance]
    for distance in range(n):
        answer[distance] >>= 1
    answer[0] = n if include_same else 0
    while len(answer) > 1 and answer[-1] == 0:
        answer.pop()
    return answer


FrequencyTableOfTreeDistance = frequency_table_of_tree_distance
