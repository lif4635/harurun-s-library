# 短い順にk本のwalk

有向グラフで、始点から終点への移動の費用を、小さい順に最大k個求める。

## 主な機能

`k_shortest_walks(vertex_count, edges, source, target, k)` は、頂点や辺を何度通ってもよいwalkを対象にする。平行辺は別の辺として数え、費用が同じでも別の辺列なら別の結果として残す。辺重みは非負。

N頂点・M辺で、時間は `O((N+M) log(N+M+2) + k log(k+1))`、メモリは `O(N+M+N log(M+2)+k)`。逆向きの最短距離を求め、最短路から外れる辺の追加費用をヒープで列挙する。

## 使い方

```python
from library_codex.shortest_path.KShortestWalks import k_shortest_walks

edges = [(0, 1, 2), (1, 1, 3), (1, 2, 4), (0, 2, 10)]
costs = k_shortest_walks(3, edges, 0, 2, 5)
assert costs == [6, 9, 10, 12, 15]
assert k_shortest_walks(2, [], 0, 1, 5) == []
```

- `costs[i]`: i+1番目に短いwalkの費用。昇順に並ぶ。
- 本数がk個に満たない場合: 存在する分だけ返す。`-1` や無限大では埋めない。
- 始点と終点が同じ場合: 辺を使わないwalkの費用0も数える。

## 注意点

- 同じ頂点を再訪しない単純パスをk本求める機能ではない。
- 費用0の閉路があっても、先頭k個で停止する。同じ費用が何度も返り得る。
- 費用だけを返す。通った辺列は復元しない。
- 整数の上限を固定していない。巨大な整数では、その演算時間も必要になる。
