# 長方形の和集合の面積

軸に平行な長方形を重ねたとき、どれか一つ以上に含まれる領域の面積を求める。

## 主な機能

- `union_rectangle_area(rectangles)` — 長方形の列から面積を求めるfunction。
- `UnionRectangle()` — `add(left, right, bottom, top)`で長方形を追加し、`run()`で現在の面積を求めるclass。

長方形1個の入力順は `(left, right, bottom, top)`。表す領域は次の半開長方形。

$$
[\mathrm{left},\mathrm{right})\times[\mathrm{bottom},\mathrm{top}).
$$

N個の面積計算は `O(N log N)` 時間、`O(N)` メモリ。座標圧縮と走査線を使うため、座標の最大値に比例する配列は作らない。

## 使い方

```python
from library_codex.spatial_structure.UnionRectangle import UnionRectangle, union_rectangle_area

rectangles = [(0, 2, 0, 2), (1, 3, 1, 3)]
assert union_rectangle_area(rectangles) == 7
area = UnionRectangle()
for rectangle in rectangles:
    area.add(*rectangle)
assert area.run() == 7
```

- 各長方形の面積は4、重なる面積は1なので、返り値は4+4-1=7。
- 返り値は面積の整数1個。重なりの回数や外周の長さではない。
- `tolist()`は追加した長方形を入力順で返すコピー。

## 注意点

- `left >= right`または`bottom >= top`の長方形は無視する。端点を自動で入れ替えない。
- 負の座標・大きな整数座標・同じ長方形の重複も扱える。整数座標なら丸め誤差はない。
- `run()`は毎回計算し直す。追加の途中で何度も呼ぶ場合、1回ごとに `O(N log N)`。
- `run()`や表示は、登録した長方形を削除・変更しない。
