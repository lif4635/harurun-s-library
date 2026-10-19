# 矩形アフィン変換と矩形和のPyPy測定

`spatial_structure/RectangleAffineSum.py`を、[Dynamic Point Set Rectangle Affine Rectangle Sum](https://judge.yosupo.jp/problem/dynamic_point_set_rectangle_affine_rectangle_sum)で検証する。点の追加・重み置換・矩形内への一次変換・矩形和を混在させる。制限時間は10秒。

## 実装と検証範囲

座標だけを先読みし、追加予定の点は無効な状態で登録する。重みの操作は入力順で処理し、有効化前の一次変換は引き継がない。任意の未登録座標を途中で追加するオンライン構造ではない。

- 末端に最大16点をまとめたKD-treeで、ノードごとのinstanceを作らない。
- 座標の種類数が極端に偏る部分では分割軸を選び直す。
- 部分的に更新する末端では、保留中の変換と新しい変換を1回の走査にまとめる。
- 重みは内部では整数だけの配列にし、無効な点を−1で持つ。公開APIでは`None`で表す。法で正規化した有効な重みは非負なので衝突しない。
- 上位の和の再計算は、矩形をたどった後の逆順走査へ分ける。再帰は使わない。

構築O(N log N)、点操作O(log N)。矩形操作は訪問ノード数Vと末端で調べる点数Kに対してO(V+K)、最悪O(N)。分割軸を適応的に選ぶため、O(sqrt N)を最悪計算量として保証しない。

公式25ケースすべてを単独コードで通過した。[専用test](../verify/spatial_structure/test_rectangle_affine_sum.py)では単純な点走査との乱択比較、空・重複座標・半開境界・細長い点群・有効化前の作用・係数0・合成数の法・表示を確認する。

## 測定条件

PyPy 3.10.14 / 7.3.16、Ryzen 7 3700X、WSL Linuxで測定。新規プロセスを逐次起動し、起動・JIT・入出力を含める。各回の出力を公式checkerで確認する。最大RSSはGNU timeで取得し、メモリ制限は強制しない。オンライン提出は行っていない。

公式revisionは`1814c4e5205517e368bb57a8d1127eb961cfeaae`。全件検証で遅かった3ケースを各5回測定した。全ケースを5回ずつ検証したという意味ではない。

## 採用版の公式反復測定

| 公式ケース | 中央値 | 最大時間 | 最大RSS |
| --- | ---: | ---: | ---: |
| many_affine_queries_00 | 7.890秒 | 8.517秒 | 139,092 KiB |
| many_random_queries_00 | 6.223秒 | 7.224秒 | 138,280 KiB |
| many_sum_queries_00 | 5.100秒 | 5.233秒 | 141,568 KiB |

## 汎用LazyKDTreeとの比較

同じ公式入力で、汎用の`LazyKDTree`にtupleとcallbackを渡した版と、今回の専用版を各5回ずつ測った。実行順は反復ごとに入れ替える。外部の上位提出との比較ではない。

| 公式ケース | 専用版の中央値 | 汎用版の中央値 | 汎用版÷専用版 |
| --- | ---: | ---: | ---: |
| max_random_00 | 4.813秒 | 27.445秒 | 5.7倍 |
| many_affine_queries_00 | 7.549秒 | 44.258秒 | 5.9倍 |
| issue_1298_00 | 1.502秒 | 55.541秒 | 37.0倍 |

分割軸・末端の点のまとめ方・整数配列・集約方法が異なるため、差の全部をcallback呼出しの有無だけに帰属させない。任意の作用・集約が必要なら汎用版を使う。ここで測っていない入力に同じ倍率を保証しない。

比較用プログラムはmoduleの読込を含むため、単独コードでの公式反復測定とは起動経路が異なる。各回の値、RSS、入力・source・checkerのhashは[比較JSON](../benchmarks/results/rectangle_affine_sum_comparison.json)に保存した。

## 試して採用しなかった変更

部分更新の再帰化、更新ループへの処理の全面展開、作用をtupleに積んで下へ運ぶ方式は、探索段階の単発測定で遅くなり採用しなかった。単発値を最終版との反復比較結果としては扱わない。整数と`None`の混在をなくした変更では、更新の多い入力が約11.1秒から約7.6秒へ短縮したが、この数値も探索段階の単発測定である。

## 再実行と記録

- [全件判定](../../verify/library_checker/results/dynamic_point_set_rectangle_affine_rectangle_sum.json)
- [公式反復測定](../../verify/library_checker/benchmarks/dynamic_point_set_rectangle_affine_rectangle_sum.json)
- [比較用プログラム](../benchmarks/rectangle_affine_sum_benchmark.py)
- [汎用LazyKDTreeによる比較用解答](../benchmarks/rectangle_affine_sum_generic.py)

```sh
pypy3 -m pytest -q library_codex/verify/spatial_structure/test_rectangle_affine_sum.py
pypy3 library_codex/tools/check_library_checker.py test dynamic_point_set_rectangle_affine_rectangle_sum --official /path/to/library-checker-problems
pypy3 library_codex/benchmarks/official_benchmark.py dynamic_point_set_rectangle_affine_rectangle_sum --official /path/to/library-checker-problems --repeat 5 --slowest 3
pypy3 library_codex/benchmarks/rectangle_affine_sum_benchmark.py --official /path/to/library-checker-problems --repeat 5 --variants generic 16
```
