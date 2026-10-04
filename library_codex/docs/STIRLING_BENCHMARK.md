# Stirling数の列の比較

2026-10-04、WSL・AMD Ryzen 7 3700X・PyPy 3.10.14 / 7.3.16で測定した。公式revisionは `1814c4e`。同一の公式入力を各5回、新しいprocessで順序を入れ替えて実行し、起動・JIT・入出力を含む中央値を比較する。全出力を公式checkerで検査した。

比較対象は、取得時点の最新問題版・AC・PyPy3・時間昇順の先頭にある、第一種の[389740 / tyuyu62](https://judge.yosupo.jp/submission/389740)と第二種の[389741 / tyuyu62](https://judge.yosupo.jp/submission/389741)。取得条件とsource hashは結果JSONに保存した。参照コードは確認してから別processで実行し、ライブラリへ転載していない。

## 採用した変更

- Kが0・1・2の場合は、FPSの冪を経由せず、階乗や線形の漸化式で計算する。
- 第一種の係数に必要な逆数を、すでに用意した階乗・逆階乗から求める。係数ごとの逆元計算を省く。
- K乗後に必要な係数までに入力FPSを切り詰める。
- 引数・返り値・modの検査条件は変えない。

Nは要素数の上限、Kはサイクル数または集合の個数。以下はすべてN=500000。

| 種類・K | 変更前 | 採用版 | 上位PyPy提出 |
| --- | ---: | ---: | ---: |
| 第一種・1 | 2.017秒 | 0.122秒 | 0.849秒 |
| 第一種・2 | 2.052秒 | 0.131秒 | 0.829秒 |
| 第一種・927 | 2.024秒 | 1.878秒 | 0.802秒 |
| 第一種・113367 | 1.951秒 | 1.843秒 | 0.819秒 |
| 第一種・500000 | 0.257秒 | 0.091秒 | 0.106秒 |
| 第二種・1 | 1.744秒 | 0.094秒 | 0.815秒 |
| 第二種・2 | 1.819秒 | 0.121秒 | 0.815秒 |
| 第二種・927 | 1.801秒 | 1.781秒 | 0.789秒 |
| 第二種・113367 | 1.767秒 | 1.816秒 | 0.803秒 |
| 第二種・500000 | 0.106秒 | 0.105秒 | 0.087秒 |

小さいKでは大きく速くなったが、一般のKでは上位実装に約2.2〜2.3倍の時間がかかる。第二種の一部は変更前より遅い。全入力で高速化したとは扱わない。参照実装はK=1・2でもFPS計算を行うため、この特殊ケースの差を一般のFPS演算の速さとはみなさない。

この5ケース中の最大RSSは、第一種が変更前175808 KiB・採用版189660 KiB・参照156872 KiB、第二種が変更前185536 KiB・採用版192312 KiB・参照152352 KiB。メモリ削減はない。

単純な漸化式で作った表との比較を専用testへ分離した。小さい素数、998244353、1000000007、符号付きの行、列の切り詰め、NTTの長さ境界、例外を検査する。

## 見送った変更

modが998244353の場合だけ専用FPSの `fps_pow` へ切り替える案も、同じ5ケースを各5回測定した。一般のKは第一種1.844〜1.845秒、第二種1.815〜1.832秒で、明確な改善は確認できなかった。依存コードも増えるため採用していない。最大RSSは一部で減るが一部では増えた。

これは測定時刻が異なる2回の比較であり、数%の差から安定した優劣は結論しない。NTT・FPS処理のどこが参照との差を生むかは、まだ特定していない。

## 記録と再実行

- 変更前: [第一種](../benchmarks/baselines/stirling_number_of_the_first_kind_fixed_k.py)、[第二種](../benchmarks/baselines/stirling_number_of_the_second_kind_fixed_k.py)
- 採用版の測定時コード: [第一種](../benchmarks/experiments/stirling_first_column_generic.py)、[第二種](../benchmarks/experiments/stirling_second_column_generic.py)
- 未採用の専用FPS版: [第一種](../benchmarks/experiments/stirling_first_column_fps998.py)、[第二種](../benchmarks/experiments/stirling_second_column_fps998.py)
- 採用版の生データ: [第一種](../benchmarks/results/stirling-first-column-comparison.json)、[第二種](../benchmarks/results/stirling-second-column-comparison.json)
- 専用FPS版の生データ: [第一種](../benchmarks/results/stirling-first-column-fps998-comparison.json)、[第二種](../benchmarks/results/stirling-second-column-fps998-comparison.json)

参照sourceはGit外のキャッシュへ保存する。再取得時には同じ提出IDとsource hashであることを確認する。

```sh
pypy3 library_codex/benchmarks/library_checker.py fetch --problem stirling_number_of_the_first_kind_fixed_k --language pypy3 --top 1 --cache ../lc-matching-reference
pypy3 library_codex/benchmarks/official_comparison.py --snapshot ../lc-matching-reference/stirling_number_of_the_first_kind_fixed_k-pypy3.json --reviewed 389740 --problem /home/harurun/.cache/harurun-library-checker/problems/enumerative_combinatorics/stirling_number_of_the_first_kind_fixed_k --cases 1_00 2_00 max_small_00 max_random_01 max_max_00 --variant baseline=library_codex/benchmarks/baselines/stirling_number_of_the_first_kind_fixed_k.py --variant candidate=library_codex/benchmarks/experiments/stirling_first_column_generic.py --repeat 5 --output library_codex/benchmarks/results/stirling-first-column-comparison.json
pypy3 library_codex/benchmarks/library_checker.py fetch --problem stirling_number_of_the_second_kind_fixed_k --language pypy3 --top 1 --cache ../lc-matching-reference
pypy3 library_codex/benchmarks/official_comparison.py --snapshot ../lc-matching-reference/stirling_number_of_the_second_kind_fixed_k-pypy3.json --reviewed 389741 --problem /home/harurun/.cache/harurun-library-checker/problems/enumerative_combinatorics/stirling_number_of_the_second_kind_fixed_k --cases 1_00 2_00 max_small_00 max_random_01 max_max_00 --variant baseline=library_codex/benchmarks/baselines/stirling_number_of_the_second_kind_fixed_k.py --variant candidate=library_codex/benchmarks/experiments/stirling_second_column_generic.py --repeat 5 --output library_codex/benchmarks/results/stirling-second-column-comparison.json
```

専用FPS案は `candidate` を上の `*_fps998.py` へ、出力先を `*-fps998-comparison.json` へ変更すると再実行できる。
