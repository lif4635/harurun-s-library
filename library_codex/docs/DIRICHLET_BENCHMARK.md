# Dirichlet積と除算の検証

`number_theory/MultiplicativeFunctions.py`の`dirichlet_multiply`と`dirichlet_divide`は、商集合の各位置までの累積和を受け取り、同じ位置での積・商の累積和を返す。数列の乗法性は不要。既存のAPIを保ち、整数・Fraction・法付き整数を扱う。

## 区間分割

[公式のDirichlet積の実装](https://github.com/yosupo06/library-checker-problems/blob/1814c4e5205517e368bb57a8d1127eb961cfeaae/number_theory/dirichlet_convolution_and_prefix_sums/sol/correct.cpp)の区間分割を使う。対角項と1を含む項は別に集計し、残りはa<bとして、商N/zに対する寄与を2通りに分ける。

- b≤zの場合: 組(a,b)の寄与は、商の値がab以上、N/b以下となる範囲へ足す。差分配列へ始点・終点だけを書き込む。
- b>zの場合: zとaを固定し、bがmax(a,z)より大きく、N/(az)以下になる範囲を累積和の差でまとめる。

前者の反復回数は次の和で抑えられる。

$$
\sum_{b\le\sqrt N}\min\left(b,\frac{N}{b^2}\right)=O(N^{2/3}).
$$

後者も、zごとの反復回数を合計すると同じオーダーになる。

$$
\sum_{z\le\sqrt N}\min\left(\sqrt{\frac Nz},\frac{N}{z^2}\right)=O(N^{2/3}).
$$

除算では除数の最初の値を1に正規化し、商の小さい位置から答えを復元する。上の区間加算は既に求めた係数だけで行え、累積和の差も現在より小さい位置しか参照しない。最後に正規化の逆数を掛ける。再帰は使わない。

積・除算はともに`O(N^(2/3))`回の算術演算、`O(sqrt(N))`追加メモリ。除算には逆元計算1回が加わる。以前の`O(N^(2/3) log(N+2))`の処理から、列挙範囲を減らした。Pythonの巨大整数・Fractionでは、算術1回の時間も値の桁数に依存する。

## 公式全件と反復測定

公式revision `1814c4e5205517e368bb57a8d1127eb961cfeaae`の積24ケース、逆元25ケースをすべて通過した。Nの上限は10¹²、時間制限はそれぞれ30秒。依存込みの単独コードをPyPyで実行し、公式checkerで照合した。オンライン提出はしていない。

全件検証で遅かった各3ケースを5回ずつ、毎回新しいprocessで逐次測定した。PyPy 3.10.14 / 7.3.16、Ryzen 7 3700X、WSL Linux。起動・JIT・入出力を含み、実行順を混ぜている。

| 問題 | 測定3ケース中で最も遅い中央値 | 15回中の最大RSS |
| --- | ---: | ---: |
| Dirichlet積と累積和 | 13.340秒 | 472412 KiB（約461 MiB） |
| Dirichlet逆元と累積和 | 10.786秒 | 343928 KiB（約336 MiB） |

30回すべて公式checkerを通過した。メモリ上限は強制していない。公式全ケースを5回ずつ測ったわけではない。

- 積: [全件判定](../../verify/library_checker/results/dirichlet_convolution_and_prefix_sums.json)、[各回の時間・RSS・入力とsourceのhash](../../verify/library_checker/benchmarks/dirichlet_convolution_and_prefix_sums.json)
- 逆元: [全件判定](../../verify/library_checker/results/dirichlet_inverse_and_prefix_sums.json)、[各回の時間・RSS・入力とsourceのhash](../../verify/library_checker/benchmarks/dirichlet_inverse_and_prefix_sums.json)

## 変更前との比較

変更前のcommit `1c37897b35ed108a1dd406ebd2c994a53dcafdf8`と比較した。法998244353、乱数seed32178で同じ商集合の累積和を作り、除数の最初の値を1に固定した。入力準備後の演算だけを計時し、毎回新しいPyPy processで各3回、実行順を混ぜている。

| 演算 | N | 変更前の中央値 | 変更後の中央値 |
| --- | ---: | ---: | ---: |
| 積 | 10¹⁰ | 2.027秒 | 0.480秒 |
| 除算 | 10¹⁰ | 0.527秒 | 0.437秒 |
| 積 | 10¹² | 30秒で打ち切り | 12.942秒 |
| 除算 | 10¹² | 12.782秒 | 10.631秒 |

打ち切りは入力準備を含むworker全体の制限で、演算だけの時間ではない。旧実装の積10¹²は1回で打ち切り、その条件の反復を停止した。速度の倍率や新旧の答えの一致は、この条件では主張しない。他の条件では、完走した新旧の答えがすべて一致した。公式ケースの検証・入出力込みの測定とは別の比較である。

[各回の値・打ち切り・答えのhash](../../verify/library_checker/benchmarks/comparisons/dirichlet.json)を保存している。スクリプトは各試行の直後に記録を保存し、途中で停止しても終了済みの測定が残る。

## 独立した検査

専用テストは、通常の整数添字で全組を足す単純解と比較する。平方数・立方数の前後、ランダム列、疎な列、零列、単位元、積からの復元、交換法則、入力非破壊、異なるN・法の拒否を含む。Fraction、法1・6・998244353・70bit超の法、逆元を持たない除数も確認する。

catalogの単独コードでも、約数個数の累積和と除算による復元を実行する。記事では、同じ表を使うMöbius関数の累積和も示す。

## 再実行

```sh
pypy3 -m pytest -q library_codex/verify/number_theory/test_multiplicative_functions.py
pypy3 library_codex/tools/check_library_checker.py test dirichlet_convolution_and_prefix_sums dirichlet_inverse_and_prefix_sums --official /path/to/library-checker-problems
pypy3 library_codex/benchmarks/official_benchmark.py dirichlet_convolution_and_prefix_sums --official /path/to/library-checker-problems --repeat 5 --slowest 3
pypy3 library_codex/benchmarks/official_benchmark.py dirichlet_inverse_and_prefix_sums --official /path/to/library-checker-problems --repeat 5 --slowest 3
pypy3 library_codex/benchmarks/dirichlet_comparison.py
```
