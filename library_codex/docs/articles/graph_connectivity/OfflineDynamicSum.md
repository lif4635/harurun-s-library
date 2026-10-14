# 辺が増減するグラフの成分和

無向グラフの辺を追加・削除しながら、頂点への加算、連結成分全体への加算、連結成分の値の総和を求める。操作を先に登録し、最後にまとめて答えを得る。

## 主な機能

`OfflineDynamicSum(values)`は、各頂点の初期値を受け取り、辺のないグラフから始める。木でなくてもよく、閉路を含むグラフに使える。

- `add_edge(u, v)` / `remove_edge(u, v)`: 辺を追加・削除する。
- `add(vertex, delta)`: 1頂点の値へ加算する。
- `add_component(vertex, delta)`: その時点でvertexとつながっている各頂点へ加算する。
- `query(vertex)`: 成分和の問い合わせを登録し、答えの添字を返す。
- `solve()`: 登録した問い合わせへの答えをlistで返す。

加算は後の辺変更でも失われない。成分が分裂しても、各頂点はそれまで加算された値を保持する。

頂点数をN、加算・問い合わせの回数をT、辺の有効期間の数をKとする。登録は1操作あたり期待・償却`O(1)`、solveは`O(N + (K log(T+1) + T) log(N+1))`時間、`O(N + T + K log(T+1))`領域。整数の加減算を定数時間として数える。

## 使い方

```python
from library_codex.graph_connectivity.OfflineDynamicSum import OfflineDynamicSum

graph = OfflineDynamicSum([1, 2, 3])
graph.add_edge(0, 1)
graph.add_component(0, 10)
first = graph.query(1)
graph.remove_edge(0, 1)
graph.add_edge(1, 2)
second = graph.query(1)
graph.add(2, 7)
third = graph.query(1)
answer = graph.solve()
assert answer == [23, 15, 22]
assert answer[first] == 23
assert answer[second] == 15
assert answer[third] == 22
```

- `answer[i]`: i番目に登録したqueryの時点の成分和。query以外の操作は添字に数えない。
- `first`などの返り値は和そのものではなく、`answer`の添字。
- 初期値の配列は変更しない。solveは繰り返し呼べ、後から操作を追加して再計算することもできる。

## 木の部分木に使う場合

木でvの親をpとすると、辺v–pを一時的に外したときのvの連結成分が、vの部分木になる。

```python
from library_codex.graph_connectivity.OfflineDynamicSum import OfflineDynamicSum

tree = OfflineDynamicSum([2, 3, 5])
tree.add_edge(0, 1)
tree.add_edge(1, 2)
tree.remove_edge(0, 1)
tree.add_component(1, 4)
index = tree.query(1)
tree.add_edge(0, 1)
assert tree.solve()[index] == 16
```

この方法は木の辺に対して使う。一般グラフでは別の経路が残ることがある。

## 仕組み

辺が存在する期間を時刻方向のセグメント木に配置し、巻き戻し可能なUnion-Findで各時点の連結成分を作る。辺の結合は巻き戻すが、頂点への加算は時刻順に残す。成分への加算は結合時の差分を記録し、分裂する際に子の成分へ渡す。

## 注意点

- 直前の答えを使って次の操作を決めるオンライン処理には使えない。木のオンライン操作には`LinkCutTree`を使う。
- 同じ無向辺を重複追加すると`ValueError`。存在しない辺の削除も`ValueError`。削除後の再追加は可能。
- 負の加算量も使える。計算は整数で行い、自動では剰余を取らない。
- 全操作を保持するため、オンラインの木構造よりメモリが多くなる場合がある。
