# 二部グラフ辺彩色の速度比較

`graph_matching/BipartiteEdgeColoring.py`の`bipartite_edge_coloring(left_size, right_size, edges)`を使う。入力辺と同じ順に色番号を返し、使用色数は最大次数に等しい。

## 実装

同じ側の頂点を次数の合計が最大次数Δ以下になる範囲でまとめ、補助辺を含めた辺数をO(E)に抑える。偶数次数なら巡回路の辺を交互に分け、奇数次数なら完全マッチングを1色として除く。時間 O(V + E√V log(Δ + 1))、追加メモリ O(V + E)。分割は明示的なスタック、辺は整数IDで管理する。

[maspyの辺彩色](https://maspypy.github.io/library/graph/bipartite_edge_coloring.hpp)と[公式解法](https://github.com/yosupo06/library-checker-problems/blob/1814c4e5205517e368bb57a8d1127eb961cfeaae/graph/bipartite_edge_coloring/sol/correct.cpp)を参考に、頂点の圧縮と偶数次数の分割を取り入れた。今回の実装は、奇数次数の部分ごとにHopcroft–Karp法で完全マッチングを求める。

`GraphProperties.bipartite_edge_coloring`も同じ処理を利用する。ただし既存の返り値`(色数, 色番号list)`は変更しない。

## 同一入力の比較

PyPy 3.10.14 / 7.3.16、Ryzen 7 3700X、WSL Linux。各入力で別processを起動し、起動・JIT・入出力込みで各5回測定した。実行順を入れ替え、全出力を公式checkerで検査した。彩色は一意でないため、出力文字列の一致は条件にしていない。

比較前はcommit `1d145c9e67d0b6fbbc34a94af780b6f4a9023f25`の`BipartiteEdgeColoring.py`。関数本体と同じ入出力を保存している。

| 公式ケース | 比較前の中央値 | 今回の中央値 | 比較前の最大RSS | 今回の最大RSS |
| --- | ---: | ---: | ---: | ---: |
| max_random_00 | 7.925秒 | 0.231秒 | 250,584 KiB | 98,736 KiB |
| large_cycle_00 | 0.188秒 | 0.160秒 | 95,504 KiB | 94,892 KiB |

`max_random_00`は左右各10万頂点・10万辺・最大次数8。旧実装は80万本へ補完してから8色を順に取り除くため、圧縮と分割の効果が大きい。一方、すでに3正則の`large_cycle_00`では差が小さい。

`worst_00`から`worst_02`は左右各10万頂点・10万辺・最大次数65535。旧実装は65億5350万本へ補完するため、メモリ保護のため比較実行しなかった。新実装はこれらを含む公式26ケースすべてを通過した。

- [各回の時間・RSS・hash](../benchmarks/results/bipartite_edge_coloring_comparison.json)
- [比較条件](../benchmarks/results/bipartite_edge_coloring_snapshot.json)
- [比較前の実装](../benchmarks/baselines/bipartite_edge_coloring_before.py)
- [公式全26ケースの検証](../../verify/library_checker/results/bipartite_edge_coloring.json)
- [遅かった3ケースを各5回測定した記録](../../verify/library_checker/benchmarks/bipartite_edge_coloring.json)

## 再実行

```sh
pypy3 library_codex/tools/check_library_checker.py test bipartite_edge_coloring --official /path/to/library-checker-problems
pypy3 library_codex/benchmarks/official_benchmark.py bipartite_edge_coloring --official /path/to/library-checker-problems --repeat 5 --slowest 3
pypy3 library_codex/benchmarks/official_comparison.py --snapshot library_codex/benchmarks/results/bipartite_edge_coloring_snapshot.json --problem /path/to/library-checker-problems/graph/bipartite_edge_coloring --cases max_random_00 large_cycle_00 --variant before=library_codex/benchmarks/baselines/bipartite_edge_coloring_before.py --variant after=verify/library_checker/solutions/bipartite_edge_coloring.py --repeat 5 --output library_codex/benchmarks/results/bipartite_edge_coloring_comparison.json
```
