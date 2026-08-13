# 区間に現れる異なる値の個数

## 主な機能

変更されない列に対して、半開区間 $[l,r)$ に一度以上現れる値が何種類あるかを求めます。queryごとに`set(values[l:r])`を作る必要はありません。

各prefixについて「その値が最後に現れた位置」だけを1として持つPersistent Segment Treeを共有します。構築は $O(N\log N)$ time・memory、`count(l, r)`は $O(\log N)$ です。

## 使い方

```python
from library_codex.range_query.StaticRangeDistinct import StaticRangeDistinct

query = StaticRangeDistinct([4, 1, 4, 2, 1, 3])

assert query.count(0, 6) == 4
assert query.count(1, 5) == 3
assert query.count(3, 3) == 0
```

要素はhashableであれば、整数以外の文字列やtupleでも使えます。

## 注意点

- 構築後の列は更新できません。
- 更新を混ぜる場合に、見かけだけ同じmethodを持つ遅い実装へ自動で切り替えることはありません。
