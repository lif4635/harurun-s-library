"""Graph-counting algorithms over a caller-selected prime modulus."""

from math import factorial

from library_codex.convolution.SetFunction import SubsetConvolution
from library_codex.math.Matrix import matrix_determinant


DEFAULT_MOD = 998244353


def _adjacency_masks(graph):
    masks = [0] * len(graph)
    for v, row in enumerate(graph):
        mask = 0
        for to in row:
            if to != v:
                mask |= 1 << to
        masks[v] = mask
    return masks


def chromatic_polynomial(graph, mod=DEFAULT_MOD):
    """Return coefficients of P(x), low degree first, in O(N 2^N).

    The modulus must admit inverses of ``1..N`` (normally a prime greater than
    N).  The inclusion-exclusion values are converted from the binomial basis
    to the ordinary power basis by forward differences.
    """
    n = len(graph)
    if n == 0:
        return [1]
    adjacency = _adjacency_masks(graph)
    size = 1 << n
    independent = [0] * size
    independent[0] = 1
    for mask in range(1, size):
        bit = mask & -mask
        v = bit.bit_length() - 1
        rest = mask ^ bit
        independent[mask] = independent[rest] and not (adjacency[v] & rest)
    independent[0] = 0
    weight = [0] * size
    weight[-1] = 1
    # ordered[k] is the number of ordered partitions into k independent sets.
    ordered = SubsetConvolution(mod).power_projection(
        independent, weight, n + 1
    )
    answer = [0] * (n + 1)
    falling = [1]
    inverse_factorial = 1
    for degree in range(n + 1):
        coefficient = ordered[degree] * inverse_factorial % mod
        for i, value in enumerate(falling):
            answer[i] = (answer[i] + coefficient * value) % mod
        if degree == n:
            break
        nxt = [0] * (len(falling) + 1)
        for i, value in enumerate(falling):
            nxt[i] = (nxt[i] - degree * value) % mod
            nxt[i + 1] = (nxt[i + 1] + value) % mod
        falling = nxt
        inverse_factorial = inverse_factorial * pow(degree + 1, -1, mod) % mod
    return answer


def evaluate_polynomial(coefficients, value, mod=DEFAULT_MOD):
    result = 0
    for coefficient in reversed(coefficients):
        result = (result * value + coefficient) % mod
    return result


def count_undirected_spanning_trees(n, edges, mod=DEFAULT_MOD):
    """Weighted/multi-edge Matrix--Tree count.

    Entries are ``(u,v)`` or ``(u,v,multiplicity_or_weight)``.
    """
    if n <= 1:
        return 1
    laplacian = [[0] * (n - 1) for _ in range(n - 1)]
    removed = n - 1
    for edge in edges:
        u, v = edge[:2]
        weight = edge[2] if len(edge) >= 3 else 1
        if u == v:
            continue
        if u != removed:
            laplacian[u][u] += weight
        if v != removed:
            laplacian[v][v] += weight
        if u != removed and v != removed:
            laplacian[u][v] -= weight
            laplacian[v][u] -= weight
    return matrix_determinant(laplacian, mod)


def count_directed_spanning_trees(n, edges, root, toward_root=True,
                                  mod=DEFAULT_MOD):
    """Count directed spanning trees rooted at ``root``.

    ``toward_root=True`` counts paths directed into the root; false counts
    paths directed away from it.  Weighted/parallel edges use their third
    tuple item as a multiplicity.
    """
    if n <= 1:
        return 1
    laplacian = [[0] * n for _ in range(n)]
    for edge in edges:
        source, target = edge[:2]
        weight = edge[2] if len(edge) >= 3 else 1
        if source == target:
            continue
        if toward_root:
            laplacian[source][source] += weight
            laplacian[source][target] -= weight
        else:
            laplacian[target][target] += weight
            laplacian[target][source] -= weight
    minor = []
    for row in range(n):
        if row != root:
            minor.append([laplacian[row][column]
                          for column in range(n) if column != root])
    return matrix_determinant(minor, mod)


def count_eulerian_circuits(n, edges, root=None, mod=DEFAULT_MOD):
    """BEST-theorem count for a directed multigraph.

    Entries are ``(u,v)`` or ``(u,v,multiplicity)``.  This matches the common
    competitive-programming normalization ``t_root * prod((out(v)-1)!)``.
    Isolated vertices are ignored; an edgeless graph has one empty circuit.
    """
    directed = []
    indegree = [0] * n
    outdegree = [0] * n
    for edge in edges:
        source, target = edge[:2]
        multiplicity = edge[2] if len(edge) >= 3 else 1
        if multiplicity < 0 or int(multiplicity) != multiplicity:
            raise ValueError("edge multiplicities must be nonnegative integers")
        multiplicity = int(multiplicity)
        if multiplicity:
            directed.append((source, target, multiplicity))
            outdegree[source] += multiplicity
            indegree[target] += multiplicity
    if indegree != outdegree:
        return 0
    active = [v for v in range(n) if outdegree[v]]
    if not active:
        return 1
    if root is None:
        root = active[0]
    if root not in active:
        return 0
    mapping = {v: i for i, v in enumerate(active)}
    compact_edges = [(mapping[u], mapping[v], multiplicity)
                     for u, v, multiplicity in directed]
    trees = count_directed_spanning_trees(
        len(active), compact_edges, mapping[root], True, mod
    )
    answer = trees
    for v in active:
        # math.factorial is fast for small degrees; reduce once per vertex.
        answer = answer * (factorial(outdegree[v] - 1) % mod) % mod
    return answer
