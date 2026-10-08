# Chordal graphの判定と証拠

長さ4以上の閉路があるとき、その閉路の隣同士でない頂点を結ぶ辺を「対角線」と呼ぶ。どの長い閉路にも対角線があるグラフがchordal graph。

## 主な機能

- `ChordalGraphRecognizer(graph)` — 無向隣接listをコピーして判定を準備するclass。
- `is_chordal()` — chordalならTrue。
- `perfect_elimination_order()` — 各頂点を除く時点で、残った隣接頂点がクリークになる除去順を返すmethod。
- `induced_cycle()` — chordalでなければ、対角線のない長さ4以上の閉路を返すmethod。

構築・最初の判定・証拠の復元はいずれもO(N+M)。結果は保存し、再呼び出しでは判定をやり直さない。頂点ごとのsetを保持せず、探索の優先度を整数配列で管理する。

## 使い方

```python
from library_codex.graph_enumeration.GraphProperties import ChordalGraphRecognizer

path = ChordalGraphRecognizer([[1], [0, 2], [1]])
assert path.is_chordal()
assert sorted(path.perfect_elimination_order()) == [0, 1, 2]
cycle = ChordalGraphRecognizer([[1, 3], [0, 2], [1, 3], [0, 2]])
assert not cycle.is_chordal()
assert set(cycle.induced_cycle()) == {0, 1, 2, 3}
```

- 除去順は頂点番号の順列。頂点ごとの時刻を返す配列ではない。
- 閉路は巡回順の頂点list。末尾と先頭にも辺があり、先頭を末尾へ重ねない。
- 成立時のinduced_cycle、不成立時のperfect_elimination_orderは空list。
- 空グラフもchordal。返すlistはコピーなので、変更しても判定器を壊さない。

## 同じmoduleに残っている辺彩色

`bipartite_edge_coloring(left_size, right_size, edges)`は別のfunctionで、判定器のmethodではない。二部多重グラフの辺を塗り、最小色数と入力辺順の色番号listを返す。chordal判定には使用しない。
