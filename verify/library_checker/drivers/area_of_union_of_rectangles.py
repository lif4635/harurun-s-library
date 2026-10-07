import sys

from library_codex.spatial_structure.UnionRectangle import union_rectangle_area

read = sys.stdin.buffer.readline
rectangles = []
for _ in range(int(read())):
    left, bottom, right, top = map(int, read().split())
    rectangles.append((left, right, bottom, top))
print(union_rectangle_area(rectangles))
