# 辺を追加しながら最小全域森を保つ

無向グラフへ辺を1本ずつ追加し、その時点での最小全域森を維持する。全辺を毎回並べ替え直さず、採用辺と重みの合計を更新できる。

## 主な機能

`forest = IncrementalMSF(n)`で辺のない状態から始め、`forest.add(u, v, weight)`で辺を追加する。1回の追加は償却O(log(N+1))時間。追加した辺の総数によらず、保持メモリはO(N)。

- `forest.weight`は現在の最小全域森の重みの合計。
- `forest.components`は連結成分数。1なら全頂点をつなぐ最小全域木になっている。
- `forest.edges()`は現在採用中の辺を取得する。

## 使い方

```python
from library_codex.graph_spanning.IncrementalMinimumSpanningForest import IncrementalMSF

forest = IncrementalMSF(3)
first = forest.add(0, 1, 5)
second = forest.add(1, 2, 8)
replaced = forest.add(0, 2, 3)
rejected = forest.add(0, 1, 9)
selected = forest.edges()
total = forest.weight
```

- `first`と`second`は`-1`。別々の成分をつなぎ、既存辺は外れない。
- `replaced`は`1`。追加順IDが1の辺`(1, 2, 8)`を、新しい辺に交換した。
- `rejected`は`3`。今回の辺自身のIDなので、不採用を表す。
- `selected`は`[(0, 0, 1, 5), (2, 0, 2, 3)]`。各tupleは`(ID, u, v, 重み)`。
- `total`は`8`。連結成分数は`1`。

## 仕組み

別々の成分を結ぶ辺はそのまま採用する。同じ成分内の辺を追加すると閉路ができるため、その両端を結ぶ現在のパスから最大重みの辺を探し、新しい辺のほうが軽ければ交換する。

内部ではAM-treeを使う。元の森とパス上の最大重みが一致する別の木を保ち、親をたどる距離が長くなりすぎないよう調整する。頂点ごとの整数配列だけを持ち、辺ごとのノードや履歴は作らない。`edges()`は内部の木の接続ではなく、入力時の端点を返す。

## 注意点

- 負の整数重み、重みの重複、平行辺に対応する。自己ループは常に不採用。
- 同じ重みの辺へは交換しない。複数の最小全域森がある場合、そのうち1つを保持する。
- IDは不採用辺も含む追加順。採用辺の添字ではない。
- 辺の削除、既存辺の重み変更、頂点追加には対応しない。
- `n`・`weight`・`components`属性は読み取り用。直接書き換えない。
- `print(forest)`で採用辺を表示できる。`edges()`はO(N + K log(K+1))時間で、Kは採用辺数。表示はさらに出力文字数に比例する時間がかかる。

## 参考

[New Algorithms for Incremental Minimum Spanning Trees and Temporal Graph Applications](https://arxiv.org/abs/2504.04619)のlazy AM-treeとPerchによる更新を、再帰を使わず実装している。同じ重みは追加順IDで区別する。
