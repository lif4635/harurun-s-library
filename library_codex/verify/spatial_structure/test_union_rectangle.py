import random

from library_codex.spatial_structure.UnionRectangle import UnionRectangle, union_rectangle_area


def test_union_rectangle_boundaries_and_repeated_run():
    assert union_rectangle_area([]) == 0
    assert union_rectangle_area([(0, 0, 0, 5), (5, 2, 0, 1)]) == 0
    assert union_rectangle_area([(0, 2, 0, 2)] * 100) == 4
    assert union_rectangle_area([(0, 1, 0, 2), (1, 3, 0, 2)]) == 6
    assert union_rectangle_area([(-10**20, 10**20, -10**20, 10**20)]) == 4 * 10**40
    for count in (1, 2, 3, 7, 8, 9, 31, 32, 33, 127, 128, 129):
        rectangles = [(i, i + 2, i, i + 2) for i in range(count)]
        original = rectangles[:]
        assert union_rectangle_area(iter(rectangles)) == 3 * count + 1
        assert rectangles == original
        assert union_rectangle_area([(a, b, 0, 1) for a, b, _, _ in rectangles]) == count + 1
    solver = UnionRectangle()
    solver.add(0, 2, 0, 2)
    assert solver.run() == solver.run() == 4
    solver.add(1, 3, 1, 3)
    assert solver.run() == 7
    assert solver.tolist() == [(0, 2, 0, 2), (1, 3, 1, 3)]
    assert str(solver) == str(solver.tolist())
    assert repr(solver) == "UnionRectangle(" + str(solver.tolist()) + ")"
    copied = solver.tolist()
    copied.clear()
    assert solver.run() == 7


def test_union_rectangle_area_against_unit_cells():
    rng = random.Random(131)
    for _ in range(20_000):
        rectangles = []
        cells = set()
        for _ in range(rng.randrange(20)):
            left, right = sorted((rng.randrange(-10, 11), rng.randrange(-10, 11)))
            bottom, top = sorted((rng.randrange(-10, 11), rng.randrange(-10, 11)))
            rectangles.append((left, right, bottom, top))
            cells.update((x, y) for x in range(left, right)
                         for y in range(bottom, top))
        assert union_rectangle_area(rectangles) == len(cells)
        solver = UnionRectangle()
        for rectangle in rectangles:
            solver.add(*rectangle)
        assert solver.run() == len(cells)
