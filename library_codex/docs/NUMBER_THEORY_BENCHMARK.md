# 整数・有理数の公式検査とPyPy測定

測定日: 2026-10-05。公式revision: `1814c4e5205517e368bb57a8d1127eb961cfeaae`。

## 今回の追加

| 問題 | 実装 | 公式ケース |
| --- | --- | ---: |
| stern_brocot_tree | 既存のSternBrocotNodeを使うdriver | 18 |
| two_square_sum | 既存のtwo_square_representationsを使うdriver | 38 |
| binomial_coefficient_prime_mod | 既存のCombを使うdriver | 20 |
| rational_approximation | FractionSearch.rational_boundsを追加 | 28 |
| min_of_mod_of_linear | MinMod.min_modを追加 | 17 |

全121ケースを公式checkerと制限時間で検査し、すべて通過した。累計159 / 253問題、3637ケース。未対応は94問題。オンライン提出は行っていない。

## 追加したアルゴリズム

`rational_bounds(x, y, limit)`は、分子・分母がどちらもlimit以下の既約分数でx/yを挟む。Stern–Brocot木の左右の境界と対象との差を保持し、連続する同方向への移動を1回の除算で処理する。整数演算を定数時間としてO(log(max(x,y)+1))時間、O(1)追加領域。

左右の境界は隣接した既約分数のままで、行列式の絶対値は1。両者の間の分数は、分子・分母がそれぞれ両端の和以上になるため、媒介分数が上限を超えた時点で両端が最適になる。対象を正確に表せる場合は同じ分数を上下へ返す。

`min_mod(n, modulus, multiplier, addend)`は、半開区間[0,n)の一次式の最小剰余を求める。剰余の折り返し直後だけを候補に残し、それを小さい法の同型問題へ変換する。必要なら列を逆順に見ることで次の法を半分以下にする。整数演算を定数時間としてO(log(modulus+1))時間、O(1)追加領域。負の係数・定数項も正規化して扱う。

どちらも既存の汎用探索を置き換えてはいない。対象が明示される場合に使える専用関数として追加した。変更前との速度比較や上位提出との比較は今回行っていない。

## 反復測定

WSL2、AMD Ryzen 7 3700X、PyPy 3.10.14 / 7.3.16。各問題で全件検査時に遅かった3ケースを各5回、計75回測定した。毎回新しいprocessで起動・JIT・入出力を含め、順序を入れ替えて逐次実行し、全出力を公式checkerで検査した。重いテストとは同時実行していない。

| 問題 | 3ケース中の最大中央値（秒） | 測定中の最大RSS（KiB） |
| --- | ---: | ---: |
| stern_brocot_tree | 0.305 | 77864 |
| two_square_sum | 0.541 | 107844 |
| binomial_coefficient_prime_mod | 0.922 | 490040 |
| rational_approximation | 0.177 | 82392 |
| min_of_mod_of_linear | 0.140 | 65904 |

二項係数は最大約479 MiBを使用している。階乗・逆階乗の2表とクエリの一括入力を使うdriverであり、省メモリ実装と比較していない。メモリ制限は強制していないため、オンラインACの保証にはしない。

各回の時間・RSS、入力とsourceのhash、測定対象名は[問題別ベンチマーク](../../verify/library_checker/benchmarks/README.md)へ保存した。反復したのは15ケースで、121ケースすべての反復測定ではない。全件の単発判定は[results](../../verify/library_checker/results)にある。

## 検査

- 専用テスト8件通過。小入力全探索、符号付き・巨大整数、無効引数、既存の単調判定探索を含む。
- 大きな有理数3000組で、上下関係・既約性・隣接分数の行列式・媒介分数が上限を超えることを確認した。
- 旧math/test_fraction_search.pyのテストをrational/test_fraction_search.pyへ移し、既存の検査を維持した。
- 通常検査166件とquick性能回帰検査が通過。今回はfull検査を再実行していない。
- API referenceとcatalogの同期、説明品質チェックが通過。368 modules、507 functions、226 classes、1428 methodsを収録。
- 再帰監査5297関数でdirect/mutual recursionなし。
- 全体の標準反復ベンチマーク保存済みは83問題。公式全件通過159問題のうち、以前の76問題はこの形式の反復測定が未保存。

## 再実行

```sh
pypy3 library_codex/tools/check_library_checker.py test stern_brocot_tree two_square_sum binomial_coefficient_prime_mod rational_approximation min_of_mod_of_linear --official /home/harurun/.cache/harurun-library-checker/problems --reuse-tests /home/harurun/.cache/online-judge-tools/library-checker-problems
pypy3 library_codex/benchmarks/official_benchmark.py stern_brocot_tree two_square_sum binomial_coefficient_prime_mod rational_approximation min_of_mod_of_linear --official /home/harurun/.cache/harurun-library-checker/problems --repeat 5 --slowest 3
pypy3 -m pytest -q library_codex/verify/number_theory/test_min_mod.py library_codex/verify/rational/test_fraction_search.py
pypy3 library_codex/tools/prepare_checkpoint.py --profile quick
```
