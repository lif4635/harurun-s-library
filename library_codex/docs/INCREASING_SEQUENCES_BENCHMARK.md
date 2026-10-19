# 上下限付き単調増加列の検証とPyPy測定

`fps/IncreasingSequences.py`の`count_increasing_sequences`を、998244353では格子経路の分割統治で計算する。長さN、単調性を補正後の値域幅Wに対し、`O(NW)`から`O((N+W) log²(N+W+2))`時間へ変更した。引数・返り値・上下限の包含関係は変えていない。998244353以外の法では従来のDPを使う。

## アルゴリズム

[noshi91の説明](https://noshi91.hatenablog.com/entry/2023/07/21/235339)と[Library Checkerの公式解](https://github.com/yosupo06/library-checker-problems/blob/1814c4e5205517e368bb57a8d1127eb961cfeaae/enumerative_combinatorics/number_of_increasing_sequences_between_two_sequences/sol/correct.cpp)を参考に、上下の境界の間を通る格子経路を階段領域と長方形へ分割する。分割統治は明示的なstack、畳み込みは既存の`NTT998`を使う。長方形だけの領域は直接変換し、小さい領域ではDPへ切り替える。

長さaの入力辺から長さbの出力辺への計算では、長さaと長さa+b−1の列の畳み込みのうち、添字a−1からa+b−2までしか使わない。変換長をa+b−1以上の最小の2冪にすれば、末尾から循環して戻る係数はa−2以下にしか届かない。そのため、通常の全係数畳み込みより小さいNTTで厳密に計算できる。

## 中央係数だけの計算との比較

PyPy 3.10.14 / 7.3.16、Ryzen 7 3700X、WSL Linux。同じ公式入力を、全係数畳み込み版と中央係数版で各5回逐次測定した。毎回新しいprocessで起動し、方式の順番を反復ごとに変え、全出力を公式checkerで照合した。起動・JIT・入出力を含む中央値。

| ケース | 全係数版 | 中央係数版 |
| --- | ---: | ---: |
| maxi_04 | 4.348秒 | 3.495秒 |
| special_00 | 4.870秒 | 3.893秒 |
| special_03 | 5.095秒 | 3.977秒 |

この3ケースでは19.6〜21.9%短縮したため中央係数版を採用した。比較対象も高速な分割統治であり、旧`O(NW)`のDPとの比較ではない。C++上位提出との実測比較でもない。

[比較の各回の時間・RSS・入力とsourceのhash](../benchmarks/results/increasing_sequences_comparison.json)。このharnessはpackageをimportするため、提出用standalone codeの測定とは起動経路が異なる。

## 公式ケースと最終版の測定

公式revisionは`1814c4e5205517e368bb57a8d1127eb961cfeaae`。長さ・値域幅とも最大131072、制限10秒の公式17ケースを、依存込みの単独コードと公式checkerで通過した。オンライン提出は行っていない。

最終版の全件検証で遅かった3ケースを各5回測定し、最大中央値は3.831秒、最大RSSは112840 KiB（約110 MiB）。起動・JIT・入出力込みで、各回の出力を公式checkerで照合した。メモリ制限は強制していない。

- [公式全17ケースの判定](../../verify/library_checker/results/number_of_increasing_sequences_between_two_sequences.json)
- [最終版の各回の時間・RSS・入力とsourceのhash](../../verify/library_checker/benchmarks/number_of_increasing_sequences_between_two_sequences.json)
- [専用テスト](../verify/fps/test_increasing_sequences.py)

専用テストでは全列挙・単純DPとの比較、非単調な境界、空列、同じ値の反復、負数、共通offsetの平行移動、法が合成数の場合、NTTの循環による混入がないことを確認する。

## 再実行

```sh
pypy3 -m pytest -q library_codex/verify/fps/test_increasing_sequences.py
pypy3 library_codex/tools/check_library_checker.py test number_of_increasing_sequences_between_two_sequences --official /path/to/library-checker-problems
pypy3 library_codex/benchmarks/official_benchmark.py number_of_increasing_sequences_between_two_sequences --official /path/to/library-checker-problems --repeat 5 --slowest 3
pypy3 library_codex/benchmarks/increasing_sequences_benchmark.py --official /path/to/library-checker-problems --repeat 5
```
