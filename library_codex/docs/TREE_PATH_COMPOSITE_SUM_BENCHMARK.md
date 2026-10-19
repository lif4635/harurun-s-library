# 木の経路合成和のPyPy測定

`tree/TreePathCompositeSum.py`を、[Point Set Tree Path Composite Sum](https://judge.yosupo.jp/problem/point_set_tree_path_composite_sum)で検証する。頂点値と辺の一次関数を置換し、任意の根へ全頂点から集めた値の和を求める。

## 実装と検証範囲

既存のStatic Top Treeを使い、一次関数の係数、順方向・逆方向の総和、頂点数を並列配列へ保持する。各頂点から根までの通過順で関数を適用し、逆向きでも逆関数にはしない。ノード用instanceや再帰は使わない。

構築O(N log N)、更新と問い合わせO(log N)、保持する整数O(N)。法での整数演算をO(1)とする。

公式26ケースすべてを単独コードで通過した。[専用test](../verify/tree/test_dynamic_tree_path_composite_sum.py)では、単純な全探索との乱択比較、パス・星・ランダム木、係数0、負数、合成数の法、深い木、表示とコピーを確認する。

## 測定条件

PyPy 3.10.14 / 7.3.16、Ryzen 7 3700X、WSL Linuxで測定。新規プロセスを逐次起動し、起動・JIT・入出力を含める。各回の出力を公式checkerで確認する。最大RSSはGNU timeで取得し、メモリ制限は強制しない。オンライン提出は行っていない。

公式revisionは`1814c4e5205517e368bb57a8d1127eb961cfeaae`。全件検証で遅かった3ケースを各5回測定した。全ケースを5回ずつ検証したという意味ではない。

## 採用版の公式反復測定

| 公式ケース | 中央値 | 最大時間 | 最大RSS |
| --- | ---: | ---: | ---: |
| typical_tree_max_02 | 2.701秒 | 2.960秒 | 249,480 KiB |
| typical_tree_max_degree_02 | 2.654秒 | 2.950秒 | 251,320 KiB |
| typical_tree_max_degree_08 | 2.430秒 | 2.595秒 | 247,628 KiB |

## 汎用DynamicRerootingDPとの比較

同じStatic Top Tree上で、tupleとcallbackを使う既存の`DynamicRerootingDP`版と、集約を配列へ分けた専用版を比較した。3ケースを各5回、反復ごとに実行順を入れ替えて測定する。外部の上位提出との比較ではない。

| 公式ケース | 専用版の中央値 | 汎用版の中央値 | 最大RSS 専用 / 汎用 |
| --- | ---: | ---: | ---: |
| typical_tree_max_01 | 1.992秒 | 4.929秒 | 275,704 / 483,528 KiB |
| typical_tree_max_02 | 3.251秒 | 7.894秒 | 268,492 / 547,752 KiB |
| typical_tree_max_degree_02 | 3.077秒 | 7.576秒 | 269,532 / 543,684 KiB |

今回の一次関数の合成和では専用版が約2.4〜2.5倍速かった。別の集約を扱うときまで同じ差を保証するものではない。

比較用プログラムはmoduleの読込を含むため、単独コードでの公式反復測定とは起動経路が異なる。各回の時間、RSS、入力・source・checkerのhashは[比較JSON](../benchmarks/results/tree_path_composite_sum_comparison.json)に保存した。

## 再実行と記録

- [全件判定](../../verify/library_checker/results/point_set_tree_path_composite_sum.json)
- [公式反復測定](../../verify/library_checker/benchmarks/point_set_tree_path_composite_sum.json)
- [比較用プログラム](../benchmarks/tree_path_composite_sum_benchmark.py)

```sh
pypy3 -m pytest -q library_codex/verify/tree/test_dynamic_tree_path_composite_sum.py
pypy3 library_codex/tools/check_library_checker.py test point_set_tree_path_composite_sum --official /path/to/library-checker-problems
pypy3 library_codex/benchmarks/official_benchmark.py point_set_tree_path_composite_sum --official /path/to/library-checker-problems --repeat 5 --slowest 3
pypy3 library_codex/benchmarks/tree_path_composite_sum_benchmark.py --official /path/to/library-checker-problems --repeat 5
```
