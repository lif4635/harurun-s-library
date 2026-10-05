# 最近点対の公式検査と比較

2026-10-05。PyPy 7.3.16 / Python 3.10.14、WSL Linux、Ryzen 7 3700X。公式問題revisionは `1814c4e5205517e368bb57a8d1127eb961cfeaae`。

## 結果

変更前は公式29ケースのうち `max_random_00` と `max_random_04` が5秒制限でTLE。変更後は29ケースすべて通過し、最大2.050秒だった。オンライン提出は行っていない。

公式3ケースを、各実装につき独立したPyPyプロセスで5回ずつ測定した。順番を入れ替えて逐次実行し、起動・JIT・入出力込みの中央値を示す。答えは毎回公式checkerで検証した。

| ケース | 変更前 | 変更後 | 参照389810 |
| --- | ---: | ---: | ---: |
| max_random_00 | 6.390秒 | 2.061秒 | 1.224秒 |
| near_grid_00 | 2.569秒 | 1.164秒 | 0.884秒 |
| max_colinear_00 | 1.605秒 | 1.760秒 | 1.067秒 |

- 大きいランダム入力は約3.10倍、格子に近い入力は約2.21倍高速化した。
- 同一直線上のケースは約9.7%遅くなった。すべての入力で速くなったわけではない。
- 比較した3ケース中の最大RSSは、変更前338176 KiB、変更後184008 KiB。約45.6%減少した。全公式ケースの最大RSSという意味ではない。
- 参照は取得時点で最新問題版のPyPy AC提出を時間順に選んだ先頭の[389810](https://judge.yosupo.jp/submission/389810)。sourceを確認し、純粋なPythonの実装として実行した。
- 参照は座標を整数へ詰めて再帰で分割する。今回の実装は再帰を使わず、座標範囲を固定しない。同距離なら添字の辞書順最小を返す仕様も保つ。参照の返す組とは異なる場合がある。
- 今回の実装は参照より約1.32〜1.68倍遅い。最速実装へ並んだとは扱わない。参照との差に、整数化・再帰・入出力・同距離の処理がそれぞれどれだけ寄与するかは未分離。

## 変更内容

- 区間ごとの辞書と候補tupleをなくし、現在の最小距離を共有する。
- 座標・入力添字・y座標順の索引を配列へ分ける。
- 併合用の配列2本を再利用する。
- 分割境界との比較で座標や距離を4倍する中間計算を避ける。
- x座標順で隣接する点から初期の上界を作る。重複点では添字の辞書順を確認して距離0を返す。

小さい乱数入力での全点対比較、等距離・重複・大きな整数座標・小数座標・不均等な区間長・入力非破壊を専用testに残した。

## 記録と再実行

- [変更前の提出コード](../benchmarks/baselines/closest_pair.py)
- [変更前の公式全件結果](../benchmarks/results/closest-pair-before.json)
- [比較の各回の時間・RSS・source hash](../benchmarks/results/closest-pair-comparison.json)
- [変更後の公式全件結果](../../verify/library_checker/results/closest_pair.json)
- [変更後の通常反復ベンチマーク](../../verify/library_checker/benchmarks/closest_pair.json)

```sh
pypy3 library_codex/tools/check_library_checker.py test closest_pair --official /home/harurun/.cache/harurun-library-checker/problems
pypy3 library_codex/benchmarks/library_checker.py fetch --problem closest_pair --language pypy3 --top 3 --cache ../lc-matching-reference
pypy3 library_codex/benchmarks/official_comparison.py --snapshot ../lc-matching-reference/closest_pair-pypy3.json --reviewed 389810 --problem /home/harurun/.cache/harurun-library-checker/problems/geo/closest_pair --cases max_random_00 near_grid_00 max_colinear_00 --variant previous=library_codex/benchmarks/baselines/closest_pair.py --variant library=verify/library_checker/solutions/closest_pair.py --repeat 5 --timeout 30 --output library_codex/benchmarks/results/closest-pair-comparison.json
pypy3 library_codex/benchmarks/official_benchmark.py closest_pair --official /home/harurun/.cache/harurun-library-checker/problems --repeat 5 --slowest 3
```

参照ランキングは変化する。再取得時は比較結果内のIDとsource hashを照合し、同じsourceであることを確認してから実行する。比較時のtimeoutは30秒で、変更前の5秒超過も測定する。公式の合否判定は5秒制限の別記録を使う。
