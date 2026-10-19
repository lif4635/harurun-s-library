# ユークリッド最小全域木の検証

`geometry/Delaunay.py`は整数座標のドロネー分割の辺を返し、`geometry/EuclideanMST.py`はその辺から最小全域木を作る。どちらも算術演算回数は`O(N log N)`、追加空間は`O(N)`。全点対の辺は作らない。

## 実装

[Library Checkerの公式実装](https://github.com/yosupo06/library-checker-problems/blob/1814c4e5205517e368bb57a8d1127eb961cfeaae/geo/euclidean_mst/sol/correct.cpp)の分割統治によるドロネー分割をPythonへ移した。座標順に分割した左右の三角形分割を、共通接線から辺を追加・削除して併合する。向きと外接円の判定は整数だけで行う。

半辺は整数IDで表し、行き先・時計回りの次辺・反時計回りの次辺を平坦な配列に保存する。逆辺はIDの下位bitを反転して求める。削除した辺の領域は再利用し、分割統治の呼出しも明示的なstackへ置き換える。頂点や辺ごとのclass instanceは作らない。

重複座標は代表点だけを三角形分割し、残りの入力点を代表点へ長さ0の辺で結ぶ。最小全域木は距離の二乗で辺をソートし、Union-FindによるKruskal法で求める。平方根を計算しないので、整数座標では辺の選択に丸め誤差が入らない。

## 公式全件と反復測定

公式revision `1814c4e5205517e368bb57a8d1127eb961cfeaae` の29ケースを、依存込みの単独コードで全て通過した。点数上限は200000、時間制限は5秒。オンライン提出は行っていない。

- [公式全件の判定と時間](../../verify/library_checker/results/euclidean_mst.json)
- [重い3ケースを各5回測った時間と最大RSS](../../verify/library_checker/benchmarks/euclidean_mst.json)

PyPy 3.10.14 / 7.3.16、Ryzen 7 3700X、WSL Linuxで測定した。各回を新しいPyPyプロセスで逐次実行し、起動・JIT・入出力を含める。ケースの順序を混ぜ、毎回公式checkerで答えを照合する。メモリ上限は強制しない。

| ケース | 5回の中央値 | 最大時間 | 最大RSS |
| --- | ---: | ---: | ---: |
| max_random_02 | 2.485秒 | 2.563秒 | 229276 KiB |
| near_grid_01 | 2.314秒 | 2.402秒 | 200824 KiB |
| max_random_07 | 2.347秒 | 2.570秒 | 228084 KiB |

15回ともcheckerを通過し、5秒以内だった。これは直前の全件検証で遅かった3ケースの反復測定であり、全29ケースを5回ずつ測った記録ではない。

## 独立した検査

- 最小全域木: 全点対の距離を直接調べるPrim法と、選択した辺の重みの多重集合を比較する。辺数・連結性・閉路がないこと・入力が変わらないことも検査する。
- 三角形分割: 辺の重複、連結性、辺の交差、辺の途中の未接続点を検査する。辺を巡って各面を復元し、内側の面が三角形であること、外接円の内部に点がないこと、Eulerの関係を確認する。
- 入力: 3×3格子の全部分集合、ランダム点と入力順の入替え、空入力、一点、重複点、共線点、同一円周上の点、巨大整数座標を含む。
- catalogとサイト: 公開関数名、返る入力番号の説明、計算量、記事、単独コード、ライセンス表記を確認する。

## 再実行

```sh
pypy3 -m pytest -q library_codex/verify/geometry/test_delaunay.py library_codex/verify/geometry/test_euclidean_mst.py
pypy3 library_codex/tools/check_library_checker.py test euclidean_mst --official /path/to/library-checker-problems
pypy3 library_codex/benchmarks/official_benchmark.py euclidean_mst --official /path/to/library-checker-problems --repeat 5 --slowest 3
```
