# 区間転倒数の速度とメモリ

2026-10-19。PyPy 7.3.16 / Python 3.10.14、WSL Linux 6.18.54.1、Ryzen 7 3700X。公式問題はrevision `1814c4e5205517e368bb57a8d1127eb961cfeaae`。WSL内の実行環境からWindows上の正本を検証し、WSL側の作業用リポジトリは更新していない。

## 採用した用途

- `OfflineRangeInversions.range_inversions(values, queries)`は問い合わせを一括処理する。Mo順とBITを使い、O(N+Q)メモリ。公式問題の解答にはこちらを採用した。
- `StaticRangeInversions(values).query(left, right)`は、前の答えを見て次の区間を決める場合にも使える。平方分割によりqueryはO(sqrt(N))だが、前計算にもO(N sqrt(N))の時間とメモリを使う。
- 両方とも重複値を転倒として数えず、半開区間を扱う。入力を変更せず、剰余を取らない整数を返す。

## 公式検査

一括処理版のstandalone解答は、`static_range_inversions_query`の公式13ケースすべてを5秒の時間制限内で通過した。重い3ケースを各5回、新しいPyPyプロセスで測定した。

| ケース | 中央値 秒 | 最大RSS MiB |
| --- | ---: | ---: |
| max_00 | 1.525 | 94.6 |
| max_01 | 1.473 | 94.9 |
| max_02 | 1.475 | 95.1 |

起動・JIT・入出力を含み、各回の出力を公式checkerで検査する。ケース順を入れ替え、逐次実行した。メモリ制限の強制とオンライン提出は行っていない。

- [全13ケースの判定](../../verify/library_checker/results/static_range_inversions_query.json)
- [3ケース各5回の時間・RSS・入力とsourceのhash](../../verify/library_checker/benchmarks/static_range_inversions_query.json)

## 同じ入力での方式比較

`max_00`と、重複値が多い`small_a_00`を各方式5回測った。共通のharnessで全問い合わせを先に読み、どの方式も同じ順の答えを出力する。起動・JIT・入出力を含み、実行順を入れ替え、全出力を公式checkerで検査した。

| 入力 | 方式 | 中央値 秒 | 最大RSS MiB |
| --- | --- | ---: | ---: |
| max_00 | 平方分割 幅317 | 2.853 | 218.2 |
| max_00 | 平方分割 幅634 | 4.242 | 157.7 |
| max_00 | Mo＋BIT | 1.905 | 114.8 |
| small_a_00 | 平方分割 幅317 | 2.781 | 216.8 |
| small_a_00 | 平方分割 幅634 | 3.642 | 156.0 |
| small_a_00 | Mo＋BIT | 1.317 | 98.4 |

この2入力では一括処理版が速く、メモリも小さい。平方分割の幅を2倍にするとメモリは減るが、問い合わせ処理が重くなった。問い合わせが既知の用途では一括処理版を使い、都度問い合わせの要件がある場合だけ平方分割版を選ぶ。

比較harnessには追加のimportと共通の入力保持があるため、上のstandalone解答の時間・RSSとは直接差し引かない。別環境や別の問い合わせ分布での優劣、Library Checkerランキングの最速実装との差を示す測定ではない。

- [各回の生データとsource hash](../benchmarks/results/range_inversions_comparison.json)
- [3方式の公式全13ケースの単発確認](../benchmarks/results/range_inversions_all_cases.json)

平方分割は[公式C++解法](https://github.com/yosupo06/library-checker-problems/blob/1814c4e5205517e368bb57a8d1127eb961cfeaae/data_structure/static_range_inversions_query/sol/correct.cpp)を基にPython化した。大きな頻度表を`array`に詰め、ブロックごとのclass instanceは作らない。出典・変更点・Apache 2.0の表記はsource、standalone code、配布ZIPへ含める。

## 再測定

リポジトリ直下から実行する。

```sh
pypy3 library_codex/tools/check_library_checker.py test static_range_inversions_query --official /home/harurun/.cache/harurun-library-checker/problems
pypy3 library_codex/benchmarks/official_benchmark.py static_range_inversions_query --official /home/harurun/.cache/harurun-library-checker/problems --repeat 5 --slowest 3
pypy3 library_codex/benchmarks/range_inversions_benchmark.py --official /home/harurun/.cache/harurun-library-checker/problems --repeat 5
```

専用testは`verify/range_query/test_offline_range_inversions.py`と`test_static_range_inversions.py`。小さい配列の全列挙、重複・負数・空区間、問い合わせ順の入れ替え、単純解とのランダム比較、32bitを超える答え、デバッグ表示と入力の非破壊性を検査する。
