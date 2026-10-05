# 等差数列の区間加算と区間最小値

## 主な機能

整数列に、位置に応じて増分が変わる区間加算を行います。
`add(left, right, slope, intercept)`は半開区間内の各要素を次のように更新します。

$$
a_i \gets a_i + \mathrm{slope}\cdot i + \mathrm{intercept}
\qquad (\mathrm{left}\le i<\mathrm{right})
$$

`query(left, right)`は、更新後の半開区間の最小値を返します。
構築は時間・メモリともに`O(N)`、加算・最小値取得はそれぞれ`O(log² N)`です。

## 使い方

```python
from library_codex.segment_tree.RangeLinearAddRangeMin import RangeLinearAddRangeMin

tree = RangeLinearAddRangeMin([5, 1, 3, 8])
tree.add(1, 4, 2, -4)
assert tree.tolist() == [5, -1, 3, 10]
assert tree.query(0, 3) == -1
```

- 増分に使う`i`は元の列のindexです。区間の左端から数え直しません。
- 左端から`first, first + step, ...`を加える場合は、`slope=step`、`intercept=first-step*left`を渡します。
- 加算は空区間にも行えます。最小値取得の区間は空にできません。
- `tolist()`は現在の値を元のindex順に並べます。取得によって状態は変わりません。

## 仕組み

各区間の点列の下側凸包を、左右の子区間を結ぶ接線で表します。
区間全体への一次式加算では凸包を構成する点の順序が変わらないため、加算を保留できます。
部分更新を行ったときだけ、境界をまたぐ区間の接線を下から作り直します。
接線の座標と保留中の係数は整数配列で保持し、nodeごとのobjectは作りません。
