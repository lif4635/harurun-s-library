# 凸包の層分解の検証

`geometry/ConvexLayers.py` の `convex_layers` と `onion_depth` は、外側の凸包から順に点を取り除く。既存の関数名、点列の順序、重複点と `keep_collinear` の扱いを保ち、既定の境界点を全て除く場合を高速化した。

## 削除可能な凸包

[Library Checkerの公式実装](https://github.com/yosupo06/library-checker-problems/blob/1814c4e5205517e368bb57a8d1127eb961cfeaae/geo/convex_layers/sol/correct.cpp)を参考に、ソートした点列を平衡二分木で分割し、各内部節点に左右の凸包を結ぶ接線の両端を保存する。左右の部分木を同時に下降すると、接線を `O(log N)` 時間で求められる。

点を除いた後は、その点の祖先だけを下から更新する。同じ層で複数点を除く場合、共通の祖先は一度だけ更新する。接線の両端が残っていれば、その接線は削除後も有効なので探索を省く。木の節点は整数IDと配列で保持し、構築・削除・境界の列挙に再帰は使わない。

一つの点の削除が影響する祖先は `O(log N)` 個で、一つの接線更新が `O(log N)`。境界列挙を含めた全体は `O(N log² N)`、追加空間は `O(N)`。整数座標では外積と整数積だけで判定する。これらは算術演算回数であり、巨大整数では桁数の影響も受ける。

`keep_collinear=False` では取得した境界から頂点だけを残し、辺の途中の点を次の層へ持ち越す。この設定の最悪時間は `O(N² log N)`。全点が共線の場合は、いずれの設定でもソート後に直接層を求める。

## 公式全件と反復測定

公式revision `1814c4e5205517e368bb57a8d1127eb961cfeaae` の21ケースを、依存込みの単独コードで全て通過した。点数上限は200000、時間制限は5秒。オンライン提出は行わず、公式checkerを使う。

- [公式全件の判定と時間](../../verify/library_checker/results/convex_layers.json)
- [重い3ケースを各5回測った時間と最大RSS](../../verify/library_checker/benchmarks/convex_layers.json)

反復測定は毎回新しいPyPyプロセスで、起動・JIT・入出力を含む。ケースの順序を混ぜて逐次実行し、各回の答えを公式checkerで照合する。メモリ上限は強制しない。公式全ケースを5回ずつ測定した記録ではない。

PyPy 3.10.14 / 7.3.16、Ryzen 7 3700X、WSL Linuxでの最終実装の測定値は次のとおり。

| ケース | 5回の中央値 | 最大時間 | 最大RSS |
| --- | ---: | ---: | ---: |
| max_random_03 | 3.352秒 | 3.538秒 | 185228 KiB |
| max_random_04 | 3.477秒 | 3.646秒 | 185160 KiB |
| max_random_02 | 3.483秒 | 3.640秒 | 184892 KiB |

15回ともcheckerを通過し、5秒以内だった。採用前の候補では反復中に5秒を超える回があり、実行環境の負荷による変動にも注意が必要。

## 変更前との比較

変更前のcommit `990aeb542ddddb34f2f77b87325ff82aaa533c77` は、層ごとに残った全点から凸包を作り直す。新旧に同じ20000点を渡し、入力準備後の `onion_depth` だけを計時する。乱数seed89172を使い、各条件を新しいPyPyプロセスで3回ずつ、順序を混ぜて測定する。

- ランダム点: 座標が0以上1000000未満の点。新旧の出力hashを比較する。
- 入れ子の正方形: 5000個の正方形の四隅。半径が大きいものから順に一層となるため、層番号を直接計算した答えとも比較する。

入力準備を含むworker全体を20秒で打ち切り、時間切れになった条件は反復を停止する。時間切れを演算時間や速度倍率へ換算しない。

| 入力 | 変更前の中央値 | 変更後の中央値 |
| --- | ---: | ---: |
| ランダム20000点 | 3.379秒 | 0.191秒 |
| 入れ子の正方形20000点 | 20秒で打ち切り | 0.121秒 |

ランダム点では完走した新旧の答えが全て一致した。正方形の旧実装は1回で打ち切っており、この入力で新旧の一致を確認したとは扱わない。新実装は3回とも直接計算した層番号に一致した。

[比較記録](../../verify/library_checker/benchmarks/comparisons/convex_layers.json)には、各回の時間、RSS、入力と答えのhash、旧sourceのhash、打ち切りを保存する。

## 独立した検査

専用テストでは、全点から毎回凸包を作る単純解と、点列の順序まで比較する。3×3格子の全部分集合、乱数、重複点、空入力、共線点、入れ子の正方形、放物線、巨大な整数座標を含む。内部の削除可能な片側凸包も、任意順の複数点削除後に単調鎖法と照合する。

catalogの単独コードで記事の例を実行し、サイトの公開用bundleとcatalogの一致、記事とAPIの表示も検査する。

## 再実行

```sh
pypy3 -m pytest -q library_codex/verify/geometry/test_convex_layers.py
pypy3 library_codex/tools/check_library_checker.py test convex_layers --official /path/to/library-checker-problems
pypy3 library_codex/benchmarks/official_benchmark.py convex_layers --official /path/to/library-checker-problems --repeat 5 --slowest 3
pypy3 library_codex/benchmarks/convex_layers_comparison.py
```
