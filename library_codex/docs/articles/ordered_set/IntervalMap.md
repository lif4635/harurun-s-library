# 区間への値の代入

## 主な機能

整数座標の半開区間へ値を割り当て、同じ値が続く部分を1区間として保持します。座標が大きくても、その長さの配列は作りません。登録の有無だけを扱う`RangeSet`と異なり、区間ごとに色・所属・状態などを持てます。

区間数Iに対して1点取得は期待O(log(I+2))、K区間を置き換える代入・削除は期待償却O((K+1) log(I+2))です。削除済み領域を定期的に回収する回はO(I log(I+2))かかります。

## 使い方

```python
from library_codex.ordered_set.IntervalMap import IntervalMap

colors = IntervalMap()
colors.assign(0, 10, "red")
colors.assign(3, 7, "blue")
assert colors.get(4) == "blue"
assert colors.items() == [(0, 3, "red"), (3, 7, "blue"), (7, 10, "red")]
assert colors.items(2, 5) == [(2, 3, "red"), (3, 5, "blue")]
assert colors.erase(4, 8) == 4
assert colors.covered_length == 6
assert colors.get(5, "missing") == "missing"
```

- `items()`は`(left, right, value)`のlistです。各組は半開区間`[left, right)`を表し、左端順に並びます。
- `erase`は実際に消した整数座標の個数を返します。区間数ではありません。
- `covered_length`は登録された整数座標の総数、`len(colors)`は圧縮した区間数です。
- 同じ値の隣接区間は結合します。`str`・`repr`で現在の区間を確認できます。

## 注意点

- 未登録の隙間は保持しません。登録値`None`と未登録を区別したい場合は、`get`のdefaultに専用の`object()`を渡してください。
- 値は等値比較できればよく、hash可能でなくても構いません。登録後に値自体を変更しないでください。
- 値は深いコピーをしません。取得した可変値を書き換えるとmap内の値も変わります。
- 範囲の逆転はエラー、空区間の代入・削除は何もしません。

## 参考

[qandori/cp-libraryのIntervalMap](https://github.com/qandori/cp-library/blob/ceec97a52d734d23f762b9c5e322b2b53df0cf9e/data_structure/interval_map.hpp)の隙間・上書き・同値結合の仕様を参照しています。
