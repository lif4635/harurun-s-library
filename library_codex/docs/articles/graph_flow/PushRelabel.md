# 最高ラベル方式の最大流

## 主な機能

非負整数の容量を持つ有向グラフで、始点から終点へ送れる最大流量を求めます。最大流を流した後は、各辺の流量と最小カットも取得できます。

高さが最大の頂点から処理するPush–Relabel法を使います。残余グラフの距離をまとめて付け直すglobal relabelと、高さの空きを利用するgap relabelを入れています。代表的な時間計算量は$O(V^2\sqrt{E})$、使用領域は$O(V+E)$です。

## 使い方

```python
from library_codex.graph_flow.PushRelabel import PushRelabel

graph = PushRelabel(4)
first = graph.add_edge(0, 1, 3)
graph.add_edge(0, 2, 2)
graph.add_edge(1, 2, 1)
graph.add_edge(1, 3, 2)
graph.add_edge(2, 3, 3)

value = graph.flow(0, 3)
edge = graph.get_edge(first)
side = graph.min_cut(0)
```

- `value`: 今回追加して流せた量。この例では5。
- `edge`: `(source, target, capacity, flow)`。この例では`(0, 1, 3, 3)`。
- `side[v]`: 最小カットの始点側に頂点`v`が含まれるか。この例では`[True, False, False, False]`。
- `graph.edges()`: `add_edge`で追加した順の辺情報。各要素は`get_edge`と同じ形式。

`flow(s, t, limit)`で、今回流す量に上限を付けられます。例えば同じグラフに`flow(0, 3, 2)`、`flow(0, 3)`の順で呼ぶと、返り値は2、3です。流した後に辺を追加してから続けることもできます。

## 実装上の扱い

- 余剰流を持つ頂点は高さ別のバケットに入れ、高いものから処理する。頂点・辺ごとの専用クラスは作らない。
- 終点へ送れなかった余剰流は始点へ戻す。終了時には途中の頂点の流入量と流出量が一致し、`get_edge`や`edges`で実際のフローを取得できる。
- 始点に固定値の$10^{18}$を与える方式ではない。容量の大きさに固定上限はなく、例えば$10^{80}$も指定できる。

## 注意点

- 容量と流量上限は非負整数。`float("inf")`は受け付けない。禁止したい切断には、有限容量の総和より大きい整数を使える。
- `min_cut(s)`は残余グラフで`s`から到達できる頂点を返す。最小カットとして使う前に、上限なしの`flow(s, t)`を最後まで流す。
- 繰り返す`flow`は同じ始点・終点を使う。返るのは累計ではなく、その呼び出しで追加して流れた量。
- `change_edge`で流量も変更する場合は、途中の頂点の流量保存を呼び出し側で保つ必要がある。
- 自己ループ・平行辺・逆向きの辺・容量0に対応する。自己ループは新たな流量を生まない。
- Dinicとの速度差は入力による。再現用の比較条件と結果は[最大流のベンチマーク](https://github.com/lif4635/harurun-s-library/blob/agent/library-codex-expansion/library_codex/docs/benchmarks/PushRelabel.md)に記録している。

## 参考

[yaketake08 / tjkendev: Push–Relabel highest selection](https://tjkendev.github.io/procon-library/python/max_flow/push-relabel-highest.html)の方式を参考に、最高ラベル選択・global relabel・gap relabelを組み込んでいます。[サイトの利用案内](https://tjkendev.github.io/procon-library/)では実装の自由利用が明記されています。

元実装の余剰流の凍結は使わず、始点への返送まで行います。既存のFIFO版はこの実装へ整理しました。現在のimportは`library_codex.graph_flow.PushRelabel`、クラス名は`PushRelabel`です。
