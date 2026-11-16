# 過去のpush・popを編集する優先度付きキュー

## 主な機能

時刻0からN-1に置いた操作を、後から挿入・削除・上書きできます。その全操作を時刻順に実行した場合、最後に残る値・個数・総和を管理します。空キューへのpopは何もしません。

構築はO(N)、1操作の編集は最悪O(log(N+2))。最後の最優先値・個数・総和はO(1)です。扱う値は整数で、負数と重複も使えます。

## 使い方

```python
from library_codex.ordered_set.RetroactivePriorityQueue import RetroactivePriorityQueue

q = RetroactivePriorityQueue(3)
q.set_push(0, 5)
q.set_pop(2)
assert q.items() == []
removed, added = q.set_push(1, 2)
assert removed == [] and added == [(0, 5)]
assert q.items() == [(0, 5)]
assert q.peek() == 5 and q.sum() == 5 and q.popped_sum() == 2
q.erase(2)
assert q.items() == [(0, 5), (1, 2)]
```

時刻1へ2の挿入を加えると、時刻2のpopは5ではなく2を取り出します。そのため、最後のキューには時刻0の5が戻ります。

- 更新の返り値は`(removed, added)`です。どちらも`(push時刻, 値)`のlistで、最後のキューへの出入りを表します。
- 追加の集計を外で持つ場合は、removedの要素を除いてからaddedを加えます。今回編集した時刻以外の要素が変わることもあります。
- `peek`は最後の最優先値、`sum`は残存値の総和、`popped_sum`は取り出される値の総和です。
- `items`は最後に残る要素をpush時刻順に返します。値順ではありません。

## 仕組み

最後に残るpushと、途中で取り出されるpushを分けます。セグ木には両者の優先度と、取り出されるpush・popの個数差を保持します。過去の1操作を編集した際に影響する少数の要素を、個数差が0になる境界から探します。

## 注意点

- 途中時刻のキューや、個々のpopの返り値は保持しません。必要なら操作列の再実行が必要です。
- `maximum=True`なら最大値を取り出します。同値は早い時刻のpushが先です。
- 時刻は固定の整数スロットです。任意時刻を使う場合は、使う時刻を先に座標圧縮します。
- 一般的なobjectの優先度比較ではなく整数用です。更新差分を使えば、値以外の付随情報の集計も外で管理できます。
- 過去の編集がない場合は`heapq`を使います。小さい操作列では、再実行の方が速い場合もあります。

## 参考

[kemunikuの部分遡及キュー](https://github.com/kemuniku/cplib/blob/f835598fec8e14039cf654a67f0244e0a654d035/src/cplib/collections/retroactive_priority_queue.nim)の境界探索と更新差分を参照し、探索を反復処理にしています。
