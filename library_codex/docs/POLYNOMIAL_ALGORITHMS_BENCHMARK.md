# 多項式の公式検査と高速化

測定日: 2026-10-05。公式revision: `1814c4e5205517e368bb57a8d1127eb961cfeaae`。

## 追加した問題

| 問題 | 公式ケース数 |
| --- | ---: |
| compositional_inverse_of_formal_power_series | 23 |
| compositional_inverse_of_formal_power_series_large | 28 |
| inv_of_polynomials | 18 |
| factorization_of_polynomials | 67 |
| polynomial_root_finding | 36 |

計172ケースを、PyPy・公式checker・公式制限時間でローカル検査した。オンライン提出は行っていない。合成逆のLargeは最大131072係数。多項式逆元は最大50000係数、根の列挙は最大4000次、因数分解は最大100次。

## 修正した処理

### 因数分解

以前の線形合同乱数の下位ビットは交互に変わるだけで、法2では同じ係数列を繰り返す場合があった。異なる既約4次式の積で停止しない例を追加し、修正前は5秒の制限で打ち切られることを確認した。`Random(seed).randrange(mod)`へ変更した後は通過した。

回帰検査には3種類の既約4次式の組合せと4種類のseedを含む。さらに、法2の次数1〜8、法3の次数1〜5のすべてのモニック多項式を、独立した試し割りと比較する。線形因子の積だけでは、この不具合を検出できなかった。

### 多項式を法とする累乗

- 同じ法多項式を反転したFPSの逆数を一度だけ計算し、累乗中の剰余計算で再利用する。
- 法多項式が小さい場合は余りを直接計算し、商を作った後に再度掛け戻す処理を省く。
- 任意の素数の法、非モニックな法多項式、負の指数は維持する。法多項式の次数63/64の切替境界も検査する。

### FPSの合成逆に使うpower projection

- 偶数次・奇数次の係数をNTT後の配列上で選び、逆変換の長さを半分にする。
- 同じ長さのNTTで使う回転係数表を各段階で再利用する。
- 次段階で不要になる係数の逆変換を省略する。
- 入力を2冪へ埋める場合の重みの位置を検査し、配列長が異なる入力や空入力も比較する。

## 上位PyPy提出との同一入力比較

2026-10-05取得時に、最新問題版でACのPyPy提出を実行時間順に取得した。実行前に全sourceを確認した。各入力を新しいPyPyプロセスで5回ずつ実行し、順番を変え、毎回公式checkerで確認した。時間は起動・JIT・入出力込みの中央値。環境はPyPy 3.10.14 / 7.3.16、WSL2、Ryzen 7 3700X。

| 対象 / 公式入力 | 修正前 | 修正後 | 上位提出 |
| --- | ---: | ---: | ---: |
| 根の列挙 / all_distinct_01 | 2.407秒 | 1.708秒 | 1.879秒 |
| 根の列挙 / max_random_04 | 1.840秒 | 1.341秒 | 1.407秒 |
| 合成逆Large / max_random_00 | 3.038秒 | 2.402秒 | 1.484秒 |
| 合成逆Large / max_random_04 | 3.152秒 | 2.385秒 | 1.472秒 |

- 根の列挙: 約27〜29%短縮。測定した2ケースでは取得した上位提出より約5〜9%速い。最大RSSは修正前約90MiB、修正後約89MiB、比較提出約92〜95MiB。
- 合成逆: 約21〜24%短縮。ただし比較提出より約62%遅く、差は未解消。最大RSSは修正前約109〜110MiB、修正後約115MiB、比較提出約128〜134MiB。変換表再利用で約5MiB増加した。
- 比較提出は根の列挙が[248175](https://judge.yosupo.jp/submission/248175)、合成逆が[367589](https://judge.yosupo.jp/submission/367589)。後者はユーザー自身の以前の提出。
- 比較したのは各2ケースであり、全問題・全入力で最速と確認したわけではない。
- 多項式逆元と因数分解には、今回上位提出との比較を行っていない。

各回の時間・RSS・入力hash・実装hash・取得時の情報は`benchmarks/results/polynomial_root_finding.json`と`benchmarks/results/compositional_inverse_of_formal_power_series_large.json`に保存した。修正前の単独実行コードは`benchmarks/baselines/`に残した。

## 公式ケースの反復測定

新規5問題は、各問題で遅かった公式3ケースを5回ずつ再測定した。次は選んだ3ケースのうち最大の中央値と、測定中の最大RSS。

| 問題 | 最大中央値 | 最大RSS |
| --- | ---: | ---: |
| 合成逆 | 0.235秒 | 79160 KiB |
| 合成逆Large | 2.392秒 | 117284 KiB |
| 多項式逆元 | 3.604秒 | 124808 KiB |
| 因数分解 | 2.791秒 | 91608 KiB |
| 根の列挙 | 1.773秒 | 92420 KiB |

公式全ケースは1回ずつ検証し、選んだ3ケースだけを反復している。反復測定を全ケースに行ったわけではない。全件の判定は`verify/library_checker/results/`、反復測定は`verify/library_checker/benchmarks/`に保存した。

## 検証範囲

- 新規5問題の172ケースに加え、依存sourceが変わった既存のFPS合成2問題も全公式ケースを再検証した。
- 累計166 / 253問題、3869ケース通過。未対応87問題。検査結果が古い問題は0。
- 変更関連テスト42件が通過。全ライブラリのfull検査はこの回では再実行していない。
- 2026-10-06の最終通常検査は166件とquick性能検査が通過。API・catalog・提出コードの同期、説明監査0件、再帰監査5502関数も確認した。
- 反復ベンチマークは新規5問題と既存のFPS合成2問題を追加し、計92問題に保存済み。以前に全件通過した74問題は、この形式の反復測定が未保存。
- API説明は因子・GCD・逆元の返り値を具体化し、因数分解・多項式剰余累乗・power projectionの記事を追加した。

## 再実行

```sh
pypy3 library_codex/tools/check_library_checker.py test compositional_inverse_of_formal_power_series compositional_inverse_of_formal_power_series_large inv_of_polynomials factorization_of_polynomials polynomial_root_finding --official /home/harurun/.cache/harurun-library-checker/problems --reuse-tests /home/harurun/.cache/online-judge-tools/library-checker-problems
pypy3 library_codex/benchmarks/official_benchmark.py compositional_inverse_of_formal_power_series compositional_inverse_of_formal_power_series_large inv_of_polynomials factorization_of_polynomials polynomial_root_finding --official /home/harurun/.cache/harurun-library-checker/problems --repeat 5 --slowest 3
pypy3 -m pytest -q library_codex/verify/fps998/test_power_projection.py library_codex/verify/fps998/test_composition.py library_codex/verify/polynomial/test_polynomial_modular_power.py library_codex/verify/polynomial/test_polynomial_factorization.py
pypy3 library_codex/tools/prepare_checkpoint.py --profile quick
```

`benchmarks/profile_compositional_inverse.py`では合成逆の処理別時間を調べられる。確認済みsourceを`--reference`、取得時のhashを`--reviewed-sha256`、公式入力を`--input`で渡す。計測を挟んだ診断用であり、上表の反復ベンチマークとは区別する。
