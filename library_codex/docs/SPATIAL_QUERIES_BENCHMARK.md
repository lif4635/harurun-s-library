# 二次元の加算・範囲和の検証

2026-10-10 JST。公式revision `1814c4e5205517e368bb57a8d1127eb961cfeaae`を固定。オンライン提出は行わない。

## 対応問題と実装

| 問題 | ライブラリ | 公式ケース |
| --- | --- | ---: |
| point_add_rectangle_sum | DynamicPointAddRectangleSum / CompressedFenwick2D | 18 |
| rectangle_add_point_get | RectangleAddPointGet | 19 |
| static_rectangle_add_rectangle_sum | RectangleAddRectangleSum | 13 |

今回の50ケースはすべて公式checkerで通過。累計192/253問題・4524ケース、未対応61問題。

`RectangleAddPointGet`は新規追加。取得する点だけ事前登録し、半開長方形への加算と一点の現在値の取得をO(log²(N+1))で行う。二次元BITの更新・集計を転置し、長方形の四隅を登録する方式と異なり、構造の大きさを取得点数Nで抑える。再帰・点ごとのnode objectは使わない。

`CompressedFenwick2D`は、y座標順の一回の走査で各行を作り、行ごとのset・sortを除いた。長方形和ではx方向・y方向とも、両端のBIT経路が合流したら打ち切る。更新座標は点の組として確認する。従来は未登録の点でも、別の点から混ざったy座標が各行にあると更新できた。現在は未登録点なら状態を変えずにKeyError。

`RectangleAddRectangleSum.solve(mod=None)`へ任意の正の法を追加した。省略時は従来どおり正確な整数値を返す。4本のBITの走査を一つにまとめ、更新eventと問い合わせeventをそれぞれ4個から2個に減らした。法指定時は係数を剰余にしてからBITへ入れ、内側のループで巨大な積を持たない。BIT内では和を正確に蓄積し、剰余演算はevent・問い合わせ単位にまとめる。

旧実装は公式10秒制限で`random_00`、`random_01`と`max_random_00`〜`02`がTLEになった。比較用に変更前のstandaloneを`benchmarks/baselines/`へ保存した。

点加算・長方形和と静的な長方形加算・長方形和の提出コードは、入力全体をsplitして保持する方式から、行単位で読む方式へ変更した。計算中に不要な入力文字列を保持しないための変更で、ライブラリのAPIは変えていない。変更後にも公式全ケースを再検証した。入力変更前の比較記録は`*_bulk_input_comparison.json`、対応するsourceは`baselines/*_bulk_input.py`に残し、source hashの一致を確認した。

## 検証内容

- 点加算・長方形和はランダム操作10,000回を単純集計と比較。
- 操作順を保持するoffline版はランダム操作5,000回を比較。
- 長方形加算・点取得は100組×200更新を全点への直接更新と比較。
- 静的な長方形加算・長方形和は100組、各100加算・100問い合わせを重なり面積の単純計算と比較。法なし・1・12・998244353を確認。
- 空、重複点、半開境界、空・逆向き長方形、負値、50桁の値、未登録点、再呼出し、デバッグ表示の非破壊性を確認。
- 依存展開済みの提出コードをpackageなしで実行し、入出力を確認。
- `prepare_checkpoint.py --profile full`が通過。PyPyの全980テスト、同期・説明監査、再帰監査6217関数、全性能回帰検査を確認した。性能閾値は緩めていない。

公式検証は公式時間制限を使う。オンラインと同じCPU・PyPyではなく、メモリ制限は強制していない。

## 比較条件

WSL Ubuntu、PyPy 3.10.14 / 7.3.16。新規processの起動・JIT・入出力を含む時間の中央値と、GNU timeによる最大RSSを記録する。各5回、実行順を固定seedで入れ替え、出力を毎回公式checkerで確認する。重いtestとは並行しない。Windowsの他アプリやCPU周波数は固定していない。

公式APIの「最新テストAC・PyPy・時間昇順」の先頭を取得し、全文を確認した。取得時点の順位であり、全言語・全入力での最速という意味ではない。

- 点加算・長方形和: [提出284920](https://judge.yosupo.jp/submission/284920)。重み更新可能なWavelet Matrixと各段のBITを使い、初期重みをまとめて構築する。
- 長方形加算・点取得: [提出285141](https://judge.yosupo.jp/submission/285141)。四隅の加算を重み付きWavelet Matrixへ載せる。
- 静的な長方形加算・長方形和: [提出285378](https://judge.yosupo.jp/submission/285378)。四隅を走査し、4係数を2組の整数へ詰めてBITで集計する。

3問とも、公式全件検証で遅かった3ケースを各5回再測定した標準記録を`verify/library_checker/benchmarks/`へ保存した。比較記録には各回の時間・RSS・入力hash・source hash・比較提出snapshotを含める。

## 点加算・長方形和の比較

| 公式ケース | 今回 秒 | 変更前 秒 | 上位PyPy 秒 | 今回 RSS KiB | 変更前 RSS KiB | 上位PyPy RSS KiB |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| max_random_00 | 2.7539 | 3.1323 | 0.8602 | 200048 | 236884 | 102204 |
| many_queries_00 | 2.7095 | 3.1999 | 0.7172 | 177552 | 223540 | 95848 |
| xy_concentrate_00 | 1.0231 | 0.9353 | 0.5713 | 129952 | 179396 | 93388 |

最初の2ケースでは変更前より約12〜15%短時間になり、最大RSSは3ケースで約16〜28%減った。ただし座標が集中するケースは約9%遅い。上位PyPy版には約1.8〜3.8倍の時間差が残っており、最速級とはいえない。重み更新可能なWavelet Matrixと初期重みの一括構築は、まだ移植していない。[各回の記録](../benchmarks/results/point_add_rectangle_sum_official_comparison.json)を保存した。

## 長方形加算・点取得の比較

| 公式ケース | 今回 秒 | 上位PyPy 秒 | 今回 RSS KiB | 上位PyPy RSS KiB |
| --- | ---: | ---: | ---: | ---: |
| max_random_00 | 2.6277 | 2.4919 | 131520 | 201124 |
| many_points_00 | 3.3561 | 1.2984 | 157824 | 161788 |
| many_rectangles_00 | 1.3006 | 3.6521 | 105576 | 230860 |

長方形が多いケースでは約2.8倍速く、最大RSSは約54%小さい。一方、取得点が多いケースでは約2.6倍遅い。今回の方式が常に上位実装より速いとはいえない。[各回の記録](../benchmarks/results/rectangle_add_point_get_official_comparison.json)を保存した。

## 静的な長方形加算・長方形和の比較

| 公式ケース | 今回 秒 | 変更前 秒 | 上位PyPy 秒 | 今回 RSS KiB | 変更前 RSS KiB | 上位PyPy RSS KiB |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| max_random_00 | 4.7520 | 17.3896 | 2.0560 | 262156 | 684364 | 273600 |
| random_00 | 3.1532 | 10.8443 | 1.4074 | 221548 | 505732 | 223940 |
| small_NQ_00 | 0.0741 | 0.0732 | 0.0763 | 60908 | 60812 | 61792 |

大きい2ケースでは変更前より約3.4〜3.7倍速く、最大RSSは約56〜62%減った。上位PyPy版と比べるとメモリは少し小さいが、時間はまだ約2.2〜2.3倍かかる。4係数の整数packingや、tupleを使わないeventの整列は未採用。[各回の記録](../benchmarks/results/static_rectangle_add_rectangle_sum_official_comparison.json)を保存した。

小さいケースは起動時間の影響が大きく、数ミリ秒の差を優劣の根拠にしない。

## 再実行

```sh
pypy3 -m pytest library_codex/verify/spatial_structure/test_compressed_fenwick_2d.py library_codex/verify/spatial_structure/test_dynamic_point_add_rectangle_sum.py library_codex/verify/spatial_structure/test_rectangle_add_point_get.py library_codex/verify/spatial_structure/test_rectangle_add_rectangle_sum.py -q
pypy3 library_codex/tools/check_library_checker.py build
pypy3 library_codex/tools/check_library_checker.py test point_add_rectangle_sum rectangle_add_point_get static_rectangle_add_rectangle_sum --official /home/harurun/.cache/harurun-library-checker/problems --reuse-tests /home/harurun/.cache/online-judge-tools/library-checker-problems
pypy3 library_codex/benchmarks/official_benchmark.py point_add_rectangle_sum rectangle_add_point_get static_rectangle_add_rectangle_sum --official /home/harurun/.cache/harurun-library-checker/problems --repeat 5 --slowest 3
```

比較sourceは公式APIから取得する。取得後に全文を確認してから実行する。下記のIDは今回確認したもの。

```sh
pypy3 library_codex/benchmarks/library_checker.py fetch --problem point_add_rectangle_sum --top 1 --cache ../lc-matching-reference
pypy3 library_codex/benchmarks/library_checker.py fetch --problem rectangle_add_point_get --top 1 --cache ../lc-matching-reference
pypy3 library_codex/benchmarks/library_checker.py fetch --problem static_rectangle_add_rectangle_sum --top 1 --cache ../lc-matching-reference
pypy3 library_codex/benchmarks/official_comparison.py --snapshot ../lc-matching-reference/point_add_rectangle_sum-pypy3.json --reviewed 284920 --problem /home/harurun/.cache/harurun-library-checker/problems/data_structure/point_add_rectangle_sum --cases max_random_00 many_queries_00 xy_concentrate_00 --variant library=verify/library_checker/solutions/point_add_rectangle_sum.py --variant previous=library_codex/benchmarks/baselines/point_add_rectangle_sum_before.py --repeat 5 --timeout 90 --output library_codex/benchmarks/results/point_add_rectangle_sum_official_comparison.json
pypy3 library_codex/benchmarks/official_comparison.py --snapshot ../lc-matching-reference/rectangle_add_point_get-pypy3.json --reviewed 285141 --problem /home/harurun/.cache/harurun-library-checker/problems/data_structure/rectangle_add_point_get --cases max_random_00 many_points_00 many_rectangles_00 --variant library=verify/library_checker/solutions/rectangle_add_point_get.py --repeat 5 --timeout 90 --output library_codex/benchmarks/results/rectangle_add_point_get_official_comparison.json
pypy3 library_codex/benchmarks/official_comparison.py --snapshot ../lc-matching-reference/static_rectangle_add_rectangle_sum-pypy3.json --reviewed 285378 --problem /home/harurun/.cache/harurun-library-checker/problems/data_structure/static_rectangle_add_rectangle_sum --cases max_random_00 random_00 small_NQ_00 --variant library=verify/library_checker/solutions/static_rectangle_add_rectangle_sum.py --variant previous=library_codex/benchmarks/baselines/static_rectangle_add_rectangle_sum_before.py --repeat 5 --timeout 90 --output library_codex/benchmarks/results/static_rectangle_add_rectangle_sum_official_comparison.json
```
