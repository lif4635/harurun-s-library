# FPS 998244353 性能監査

この文書は `library_codex.fps998` と、その周辺の 998244353 専用多項式演算を、Library Checker の問題・上位提出・代表的な高速ライブラリと演算ごとに比較した記録です。

比較日は 2026-08-10 です。Library Checker の順位と実行時間は変動するため、提出 ID も併記します。C++ と PyPy の秒数はアルゴリズム選定の参考に使い、ローカル PyPy の秒数と直接割り算はしません。

## 比較方法

- 最大入力は [Library Checker Problems](https://github.com/yosupo06/library-checker-problems) の `task.md`・`info.toml`・verifier を正本とする。
- 最速提出は [Library Checker Judge API](https://github.com/yosupo06/library-checker-judge/blob/master/restapi/openapi/openapi.yaml) の `status=AC`, `dedupUser=true`, `order=+time` で C++23 と PyPy3 を取得する。
- 上位提出のソースを読み、理論計算量だけでなく、Newton 法の状態再利用、NTT 回数、積木の表現、Python の剰余頻度を比較する。
- 実装の比較対象として [Nyaan's Library](https://github.com/NyaanNyaan/library) と [suisen-cp library](https://github.com/suisen-cp/cp-library-cpp) も確認する。
- ローカル計測は WSL x86_64、PyPy 7.3.16 / Python 3.10.14。入出力時間は含めない。

## Library Checker 上位提出のスナップショット

| 演算 | 最大入力 | C++ 最速 | PyPy 最速 |
| --- | ---: | ---: | ---: |
| convolution | `N,M <= 524288` | [305538](https://judge.yosupo.jp/submission/305538) 0.024 s | [140260](https://judge.yosupo.jp/submission/140260) 0.338 s |
| FPS inverse | `N <= 500000` | [261768](https://judge.yosupo.jp/submission/261768) 0.027 s | [140558](https://judge.yosupo.jp/submission/140558) 0.345 s |
| FPS logarithm | `N <= 500000` | [261769](https://judge.yosupo.jp/submission/261769) 0.032 s | [319265](https://judge.yosupo.jp/submission/319265) 0.500 s |
| FPS exponential | `N <= 500000` | [261766](https://judge.yosupo.jp/submission/261766) 0.038 s | [319294](https://judge.yosupo.jp/submission/319294) 0.593 s |
| FPS power | `N <= 500000` | [382181](https://judge.yosupo.jp/submission/382181) 0.052 s | [389195](https://judge.yosupo.jp/submission/389195) 0.862 s |
| FPS square root | `N <= 500000` | [248686](https://judge.yosupo.jp/submission/248686) 0.025 s | [389198](https://judge.yosupo.jp/submission/389198) 0.408 s |
| polynomial division | `N,M <= 500000` | [285073](https://judge.yosupo.jp/submission/285073) 0.030 s | [389212](https://judge.yosupo.jp/submission/389212) 0.566 s |
| FPS composition large | `N <= 131072` | [247871](https://judge.yosupo.jp/submission/247871) 0.149 s | [367593](https://judge.yosupo.jp/submission/367593) 2.555 s |
| compositional inverse large | `N <= 131072` | [249758](https://judge.yosupo.jp/submission/249758) 0.117 s | [367589](https://judge.yosupo.jp/submission/367589) 1.603 s |
| multipoint evaluation | `N,M <= 131072` | [340010](https://judge.yosupo.jp/submission/340010) 0.039 s | [263081](https://judge.yosupo.jp/submission/263081) 0.477 s |
| polynomial interpolation | `N <= 131072` | [261773](https://judge.yosupo.jp/submission/261773) 0.055 s | [389214](https://judge.yosupo.jp/submission/389214) 1.321 s |
| Taylor shift | `N <= 524288` | [146805](https://judge.yosupo.jp/submission/146805) 0.033 s | [389216](https://judge.yosupo.jp/submission/389216) 0.349 s |
| product of polynomial sequence | `sum degree <= 500000` | [173781](https://judge.yosupo.jp/submission/173781) 0.158 s | [137778](https://judge.yosupo.jp/submission/137778) 1.935 s |
| find linear recurrence | `N <= 10000` | [196170](https://judge.yosupo.jp/submission/196170) 0.015 s | [389235](https://judge.yosupo.jp/submission/389235) 0.186 s |

## 演算別の監査結果

| 演算 | 現在の方式 | 上位実装との比較 |
| --- | --- | --- |
| convolution | 998244353 固定 radix-4 NTT。通常は 2 forward + 1 inverse。同じ入力の二乗は 1 forward + 1 inverse。 | 同じ構成。出力長が 2 の冪を少し越える場合は、短い末尾だけ直接加算して NTT 長の倍増を避ける。 |
| inverse | Newton 倍化。変換済みの逆数を再利用し、各倍化 2 forward + 2 inverse。 | Nyaan・suisen の NTT-friendly inverse と同じ状態再利用。 |
| logarithm | `integral(diff(f) * inv(f))`。 | 上位 PyPy と同じ。inverse は上記の高速経路を使う。 |
| exponential | exponential とその inverse を同時に倍化する NTT-friendly 法。 | 上位 PyPy と Nyaan の実装と同じ中核手順。単純な `exp(f-log(g))` Newton には戻さない。 |
| power | 先頭ゼロを処理し、単元化して `exp(k log f)`。疎なら `O(NK)` 漸化式。 | 密入力は上位実装と同じ。疎入力は NTT との実測交点を演算別閾値にしている。 |
| square root | root と inverse(root) を同時に倍化する Newton 法。 | 以前は各段で inverse を先頭から再計算していた。suisen 型の変換再利用へ変更済み。 |
| FPS division | denominator inverse を 1 回作り convolution。 | 標準高速形。多項式としての商・余りとは API を分離。 |
| polynomial division | 反転、inverse、convolution。余りは商と divisor の積から作る。 | Library Checker 上位の標準形と同じ。小さい divisor は直接除算。 |
| composition | 分割統治 `O(N log^2 N)`。再帰は使わず明示 stack。下降時の NTT 結果を上昇時に再利用。 | Nyaan の fast composition と同じ理論計算量。Large の PyPy 最速系統と同じ方式。 |
| compositional inverse | Lagrange inversionを power projection、log、exp へ帰着。 | Nyaan の compositional inverse と同じ `O(N log^2 N)` 系統。互換 alias は置かない。 |
| power projection | 分割統治で P と Q の NTT を同段共有。 | 公開 Library Checker に単変数版の直接問題はないが、composition inverse の内部演算として変換回数を監査。 |
| multipoint evaluation | 998 専用の NTT 表現積木。root inverse は 1 回だけ作り、剰余情報を積木へ伝播。 | 一般 mod 版の節点ごとの除算から分離。Nyaan `FastMultiEval` と上位 PyPy の transposed product-tree 系統。 |
| interpolation | 積多項式の微分値を高速多点評価し、一括逆元後に平衡 merge。 | 上位 PyPy と同じ構成。一般 mod 版も維持。 |
| Taylor shift | factorial / inverse factorial を用いる 1 回の convolution。 | 上位実装の標準形と同じ。 |
| polynomial sequence product | 長さが同じ入力は level ごとの平衡 merge。長さが異なる場合は Huffman 型 heap merge。 | 一次式 50 万本で heap 操作を 50 万回行う無駄を除去。 |
| Berlekamp--Massey | `O(N^2)`。discrepancy の加算中は 8 項ごとに剰余。 | 最速 PyPy 提出と同じ剰余頻度。half-GCD はこの制約と PyPy では定数倍が重く、採用していない。 |
| Bostan--Mori | P, Q の forward NTT を共有し、1 段 4 transforms。 | 独立 convolution 2 回の 6 transforms から削減済み。 |

## 今回の変更前後

同じ WSL / PyPy、同じ決定的入力での中央値または単回計測です。

| 演算 | 入力 | 変更前 | 変更後 | 改善 |
| --- | ---: | ---: | ---: | ---: |
| FPS square root | `N=131072` | 0.3166 s | 0.1129 s | 2.80x |
| multipoint evaluation | `N=M=131072` | 2.7365 s | 0.9219 s | 2.97x |
| interpolation（木構築を含む） | `N=131072` | 約 3.40 s | 約 2.21 s | 1.54x |
| Berlekamp--Massey | `N=10000`, degree 5000 | 0.4369 s | 0.1019 s | 4.29x |
| 2 の冪境界直後の convolution | output `131073` | 0.0785 s | 0.0353 s | 2.22x |
| 一次式の product | 500000 本 | 3.6409 s | 1.9669 s | 1.85x |

## Library Checker 最大プロファイル

`benchmark_fps998_library_checker.py --profile library-checker` の実測です。

| 演算 | N | 秒 |
| --- | ---: | ---: |
| convolution | 524288 | 0.314 |
| inverse | 500000 | 0.465 |
| logarithm | 500000 | 0.771 |
| exponential | 500000 | 0.809 |
| power | 500000 | 1.533 |
| square root | 500000 | 0.505 |
| polynomial division | 500000 | 0.504 |
| composition | 131072 | 2.469 |
| compositional inverse | 131072 | 2.776 |
| power projection | 131072 | 2.449 |
| multipoint evaluation | 131072 | 1.066 |
| interpolation | 131072 | 2.211 |
| Taylor shift | 524288 | 0.306 |
| product of degree-one polynomials | 500000 | 1.812 |
| Berlekamp--Massey | 10000 | 0.116 |
| recurrence nth | order 5000 | 0.223 |

## 再計測

```bash
pypy3 library_codex/tools/benchmark_fps998_library_checker.py --profile quick
pypy3 library_codex/tools/benchmark_fps998_library_checker.py --profile library-checker
pypy3 library_codex/tools/benchmark_fps998_library_checker.py --profile library-checker --operations sqrt,multipoint,berlekamp_massey --repeat 3
pypy3 library_codex/tools/benchmark_fps998_library_checker.py --profile quick --json
```

秒数そのものを固定した test にはしません。正しさは randomized test と最大入力 test、性能退行はこのベンチの履歴で確認します。
