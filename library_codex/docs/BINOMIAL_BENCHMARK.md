# 任意法・q二項係数の検査と高速化

測定日: 2026-10-05。公式revision: `1814c4e5205517e368bb57a8d1127eb961cfeaae`。

## 対象

- `binomial_coefficient`: 任意の正の法、nは最大10^18。公式30ケース。
- `q_binomial_coefficient_prime_mod`: qと素数の法が固定、n・kは法未満。公式30ケース。

両問題とも全公式ケースをローカルcheckerと公式制限時間で通過。累計161 / 253問題、3697ケース。残り92問題。オンライン提出は行っていない。

## 実装の変更

### 任意法の二項係数

- 素因子を除いた階乗に加え、逆階乗も表へ保存する。問い合わせごとの逆元計算をなくした。
- n・k・n-kを同じループでp進方向へ縮め、繰り上がり数を数える。法の指数以上なら0を返す。
- CRTの係数は法ごとに構築時に計算し、問い合わせ時は剰余との積を足すだけにした。
- 階乗表は遅延生成を維持し、必要な添字に応じて幾何的に拡張する。大きな素数の法でも、C(p,1)=0やC(p+1,1)=1のためだけにp要素の表を確保しない。
- 大きな素数向けのLargePrimeFactorialは従来の方式を維持した。今回の公式問題の範囲は法1000000以下であり、この分岐の大規模性能は今回比較していない。

### q二項係数

- 高位部分の通常二項係数を整数全体として作る`math.comb`を除去。法の上で前計算し、必要ならLucasの定理で桁ごとに求める。
- q整数を保存する作業配列をなくし、逆順の漸化式で逆階乗を構築する。
- q=0は表なしで処理。q=1は通常の階乗・逆階乗を直接構築し、追加のq演算と一時配列を省く。
- 小さい素数の法でnが法以上の場合も検査した。周期が判明している場合は、準備範囲より大きいnも桁ごとの積で処理する。
- 周期が未判明で、準備済みの表を超えるnはValueErrorにした。従来は仮の周期で誤った値を返す可能性があった。互換aliasは追加していない。

## 比較方法

WSL2、AMD Ryzen 7 3700X、PyPy 3.10.14 / 7.3.16。同じ公式入力を各実装で5回ずつ測定。毎回新しいprocessで起動・JIT・入出力を含め、実行順序を入れ替え、すべて公式checkerで判定した。重い検査とは同時実行していない。

参照したのは、取得時点で最新の問題versionを通過していた最速PyPy提出の[389735](https://judge.yosupo.jp/submission/389735)と[389784](https://judge.yosupo.jp/submission/389784)。取得後にsource全体を読んでから実行した。公式C++解答の素数冪階乗・q二項係数の分解も確認した。

任意法は変更前の提出コードを`benchmarks/baselines/binomial_coefficient_before.py`へ保存し、新旧と参照実装を同じ入力で比較した。q二項係数は変更前との反復比較ではなく、更新版と上位実装の比較。

両者のdriverは入力方法・表の準備範囲も異なるため、差をすべてライブラリ内部の演算速度の差とは扱わない。出力の末尾改行が異なるため生の出力hashが違う場合があるが、すべて公式checkerを通過している。

### 同一入力の中央値（秒）

| 任意法のケース | 変更前 | 更新版 | 参照389735 |
| --- | ---: | ---: | ---: |
| m_510510_n_max_00 | 3.695 | 0.646 | 0.591 |
| m_524288_n_max_00 | 3.593 | 1.096 | 0.760 |
| max_random_04 | 3.547 | 0.582 | 0.537 |

更新版は変更前の約3.3〜6.1倍速い。ただし2冪のケースでは参照より約44%遅く、最大RSSも更新版91148 KiB、参照80980 KiBだった。残る定数倍の差は解消済みとはしない。

| q二項係数のケース | 更新版 | 参照389784 | 更新版RSS（KiB） | 参照RSS（KiB） |
| --- | ---: | ---: | ---: | ---: |
| mod998244353_q2_maxi_00 | 1.176 | 1.124 | 365440 | 402008 |
| small_ord_00 | 0.648 | 0.642 | 372780 | 280384 |
| q_01_01 | 0.746 | 0.855 | 411872 | 367760 |

小さい位数のケースでは時間が近い一方、更新版のRSSは約33%多い。q=1では更新版が速いが、RSSは約12%多い。速度だけで全面的に優れるとはしない。

標準の公式ベンチマークも別に実施し、各問題の遅い3ケースを各5回、計30回保存した。その最大中央値は任意法1.142秒、q二項係数1.198秒。上位比較は任意法45回・q二項係数30回の計75回。全60ケースを反復したわけではない。

メモリは測定中の最大RSS。メモリ制限は強制していない。手元とオンラインjudgeでは環境が異なるため、オンラインACや最悪時間の保証にはしない。

## 検査

- 専用テスト7件通過。小さい全法の通常二項係数、小さい素数ごとの全qのPascal漸化式、法を超えるn、表の拡張・巨大整数・不正入力を含む。
- 旧mathカテゴリの任意法テストと、混在していたq二項係数テストをcombinatorics専用ファイルへ移し、既存の検査を維持した。
- 通常検査166件とquick性能回帰検査が通過。今回はfull検査を再実行していない。
- API reference・catalog・提出コードの同期と説明品質チェックが通過。368 modules、507 functions、226 classes、1428 methodsを収録。
- 再帰監査5379関数でdirect/mutual recursionなし。
- 全体の標準反復ベンチマーク保存済みは85問題。以前に全件通過した76問題は、この形式の反復測定がまだ未保存。

## 再実行

```sh
pypy3 library_codex/tools/check_library_checker.py test binomial_coefficient q_binomial_coefficient_prime_mod --official /home/harurun/.cache/harurun-library-checker/problems --reuse-tests /home/harurun/.cache/online-judge-tools/library-checker-problems
pypy3 library_codex/benchmarks/official_benchmark.py binomial_coefficient q_binomial_coefficient_prime_mod --official /home/harurun/.cache/harurun-library-checker/problems --repeat 5 --slowest 3
pypy3 -m pytest -q library_codex/verify/combinatorics/test_arbitrary_binomial.py library_codex/verify/combinatorics/test_q_binomial.py
pypy3 library_codex/tools/prepare_checkpoint.py --profile quick
```

上位比較のsource hash、取得時の情報、入力hash、各回の時間とRSSは`benchmarks/results/binomial_coefficient.json`と`benchmarks/results/q_binomial_coefficient_prime_mod.json`に保存した。比較入力は前者が`m_510510_n_max_00 m_524288_n_max_00 max_random_04`、後者が`mod998244353_q2_maxi_00 small_ord_00 q_01_01`。
