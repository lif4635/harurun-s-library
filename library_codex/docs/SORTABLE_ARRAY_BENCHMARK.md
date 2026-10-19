# 区間ソートと区間積のPyPy測定

`sequence_structure/SortableArray.py`を、[Point Set Range Sort Range Composite](https://judge.yosupo.jp/problem/point_set_range_sort_range_composite)の公式入力で検証する。キー・一次関数の置換、関数合成、昇順・降順ソートを混在させる問題で、配列長と操作数はそれぞれ最大100,000、制限時間は10秒。

## 実装と検証範囲

ソート済み区間ごとのtreapに順方向・逆方向の積を置き、区間境界はFastSet、区間間の集約はSegTreeで管理する。要素ごとのclass instanceは使わず、要素数Nに対してN個のノードを平坦な配列で持つ。分割・統合・置換でノードを増やさず、再帰も使わない。

汎用APIは任意の結合的演算を受け取る。公式driverでは一次関数の2係数を整数1つへ詰めている。キーと値が同時に移動すること、文字列連結による非可換な積、空配列、重複キーの拒否、表示後の状態、繰り返しの分割・統合は[専用test](../verify/sequence_structure/test_sortable_array.py)で確認する。

公式revisionは`1814c4e5205517e368bb57a8d1127eb961cfeaae`。公式23ケースすべてを依存込みの単独コードで通過した。オンライン提出は行っていない。

## 測定方法

PyPy 3.10.14 / 7.3.16、Ryzen 7 3700X、WSL Linuxで測る。新規プロセスを逐次起動し、JIT・起動・入出力を含める。入力順を反復ごとに入れ替え、毎回公式checkerで出力を確認する。メモリはGNU timeの最大RSSで、メモリ制限は強制しない。

- 公式反復測定: 全件検証で遅かった3ケースを各5回。
- 方式比較: 最大ランダム、区間積が多いケース、降順ソートが多いケースを各5回。
- `full_pull`: 集約値を更新するとき、分岐を挟まず4回のモノイド演算を行う採用版。
- `skip_identity`: 子が空なら単位元との演算を省く比較版。比較用の関数をbenchmark内へ残す。

比較用プログラムはmoduleの読込を含むため、単独の公式driverとは起動時間が異なる。外部の上位提出との比較ではない。

## 採用版の公式反復測定

| 公式ケース | 中央値 | 最大時間 | 最大RSS |
| --- | ---: | ---: | ---: |
| max_random_00 | 4.117秒 | 4.815秒 | 97,756 KiB |
| max_random_01 | 4.250秒 | 4.601秒 | 98,364 KiB |
| max_random_02 | 4.363秒 | 4.651秒 | 100,992 KiB |

全23ケースの反復ではなく、全件検証で遅かった3ケースを各5回測った結果。入力・source・checkerのhashと各回の値はJSONに保存している。

## 集約更新の比較

| 公式ケース | 採用版の中央値 | 単位元の演算を省く版 |
| --- | ---: | ---: |
| max_random_01 | 4.567秒 | 4.580秒 |
| many_1_query_01 | 4.243秒 | 4.259秒 |
| many_3_query_01 | 3.463秒 | 3.736秒 |

各5回の比較で、最初の2ケースの差は約0.3%と小さかった。降順ソート中心のケースでは採用版が約7%短時間だった。今回の一次関数合成では演算を省く分岐に一貫した利点がなかったため、分岐なしを採用する。高コストの別のモノイドで同じ結果になるとは限らない。

## 記録と再実行

- [公式全件判定](../../verify/library_checker/results/point_set_range_sort_range_composite.json)
- [公式反復測定](../../verify/library_checker/benchmarks/point_set_range_sort_range_composite.json)
- [実装方式の比較](../benchmarks/results/sortable_array_comparison.json)

```sh
pypy3 -m pytest -q library_codex/verify/sequence_structure/test_sortable_array.py
pypy3 library_codex/tools/check_library_checker.py test point_set_range_sort_range_composite --official /path/to/library-checker-problems
pypy3 library_codex/benchmarks/sortable_array_benchmark.py --official /path/to/library-checker-problems
pypy3 library_codex/benchmarks/official_benchmark.py point_set_range_sort_range_composite --official /path/to/library-checker-problems --repeat 5 --slowest 3
```
