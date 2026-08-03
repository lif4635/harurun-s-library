"""複数の有理形式的冪級数を1つの分子・分母へまとめる。"""

from heapq import heapify, heappop, heappush

from library_codex.fps.FormalPowerSeries import (
    DEFAULT_MOD,
    fps_add,
    fps_exponential,
    fps_inverse,
    fps_logarithm,
    fps_multiply,
)

def sum_of_rationals(fractions, mod=DEFAULT_MOD):
    """Combine pairs (numerator, denominator) into a single rational FPS."""
    if not fractions:
        return [0], [1]
    heap = []
    for serial, (numerator, denominator) in enumerate(fractions):
        if not denominator:
            raise ZeroDivisionError("a rational FPS denominator is zero")
        numerator = [value % mod for value in numerator]
        denominator = [value % mod for value in denominator]
        heap.append((len(numerator) + len(denominator), serial,
                     numerator, denominator))
    heapify(heap)
    serial = len(heap)
    while len(heap) > 1:
        _, _, first_numerator, first_denominator = heappop(heap)
        _, _, second_numerator, second_denominator = heappop(heap)
        numerator = fps_add(
            fps_multiply(first_numerator, second_denominator, mod),
            fps_multiply(first_denominator, second_numerator, mod),
            mod,
        )
        denominator = fps_multiply(first_denominator, second_denominator, mod)
        heappush(heap, (len(numerator) + len(denominator), serial,
                        numerator, denominator))
        serial += 1
    _, _, numerator, denominator = heap[0]
    return numerator, denominator

