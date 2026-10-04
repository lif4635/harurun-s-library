# 要素を変更できる区間頻度

## 主な機能

列の1要素を置き換えながら、半開区間内に指定した値が何個あるか数える。初期構築は O(N)、更新・検索は O(sqrt(N+1))、使用領域は O(N)。辞書の操作を O(1) としている。

## 使い方

```python
from library_codex.ordered_set.PointSetRangeFrequency import PointSetRangeFrequency

freq = PointSetRangeFrequency([2, 1, 2, 3])
before = freq.query(0, 3, 2)
freq.set(1, 2)
after = freq.query(1, 4, 2)
```

- `before`: `[2, 1, 2]` に含まれる2の個数で、2。
- `after`: 更新後の区間 `[2, 2, 3]` に含まれる2の個数で、2。
- `set` は値を返さず、以降の検索に変更を反映する。

## 注意点

- 要素は整数に限らず、辞書のキーにできる値を使える。
- 初期値はコピーする。元の列を後から変更しても反映されない。
- 列の長さは固定。挿入・削除は扱わない。
- 値ごとに出現位置を昇順の小さな配列へ分けて持つ。大きくなった配列は分割し、小さくなった隣接配列は結合する。出現しなくなった値は辞書から除く。
