# 追加機能とベンチマーク

`library_codex` を参照元4ライブラリの外へ広げ、既存APIを壊さずに追加した機能をまとめる。
すべて非再帰・標準ライブラリのみで動作する。

## Advanced Flow

`graph_flow/AdvancedFlow.py`

- global relabel付きFIFO push-relabel最大流
- `flow(source, sink, flow_limit)` による部分流・反復実行
- Gomory--Hu cut tree
- Stoer--Wagner global minimum cut
- 小規模全列挙min-cut、既存Dinic、長さ100,000のpathで検証

ベンチマークは `tools/benchmark_advanced_flow.py` で実行できる。
Push-relabelはグラフ族によって既存Dinicとの優劣が入れ替わるため、一律置換はしない。

| 頂点数 | 辺数 | 既存Dinic | Push-relabel | Dinic / Push-relabel |
| ---: | ---: | ---: | ---: | ---: |
| 500 | 7,505 | 0.007220 s | 0.003562 s | 2.027x |
| 300 | 10,811 | 0.002781 s | 0.005081 s | 0.547x |

## CSR Graph

`graph/CSRGraph.py`

- 有向・無向、重み、平行辺、自己loop、元edge IDを保持するimmutable CSR
- 対称な無向隣接listを検証しながら変換する `from_adjacency`
- Dijkstra / 0-1 BFS / BFS
- topological sort / connected components / bipartite coloring
- SCC
- LowLink
- 100,000頂点pathと既存実装とのランダム比較で検証

ベンチマークは `tools/benchmark_csr_graph.py` で実行できる。
PyPy 7.3.16、100,000頂点・500,000辺での結果。

| algorithm | list合計 | CSR合計 | 高速化 | list RSS | CSR RSS | RSS削減 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Dijkstra | 0.607686 s | 0.323569 s | 1.88x | 166,224 KiB | 155,960 KiB | 6.2% |
| SCC | 0.661704 s | 0.214567 s | 3.08x | 186,244 KiB | 153,796 KiB | 17.4% |
| LowLink | 0.585286 s | 0.195264 s | 3.00x | 206,228 KiB | 182,632 KiB | 11.4% |

辺を逐次追加する場合は既存隣接list、大きい静的グラフはCSR版を使う。

## Integer Range Tree

`data_structure/IntRangeTree.py`

- `RangeAddAssignRangeStats`: range add/assign、sum/min/max
- `RangeAffineRangeSum`: range affine、range sum、任意modulus
- 愚直list、200,000要素、素数法・合成数法・法なしで検証

ベンチマークは `tools/benchmark_int_range_tree.py` で実行できる。
PyPy 7.3.16、200,000要素・200,000操作での結果。

| workload / backend | 合計時間 | 専用版に対する比 | 最大RSS |
| --- | ---: | ---: | ---: |
| stats / 汎用Lazy Segment Tree | 6.586086 s | 3.77x | 273,064 KiB |
| stats / Segment Tree Beats | 5.789948 s | 3.31x | 192,840 KiB |
| stats / `RangeAddAssignRangeStats` | 1.748529 s | 1.00x | 130,572 KiB |
| affine / 汎用Lazy Segment Tree | 1.928523 s | 1.97x | 152,728 KiB |
| affine / `RangeAffineRangeSum` | 0.978862 s | 1.00x | 117,644 KiB |

自由な演算は既存 `LazySegmentTree`、chmin/chmaxも必要なら `SegmentTreeBeats`、
対応する頻出整数操作だけなら専用版を使う。

## 性能回帰チェック

- `tools/run_benchmarks.py`: 各ベンチマークを一括実行する
- `tools/benchmark_baseline.json`: quick/full profileの最低速度比
- backend間のchecksumも比較し、答えが異なる場合は失敗する
- `--output result.json` で計測結果をJSON保存できる

通常の短い確認は次で実行する。

```bash
pypy3 library_codex/tools/run_benchmarks.py --profile quick
```

基準計測は `--profile full` を使う。
