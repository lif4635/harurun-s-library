# 乗法的関数の総和の検証

`number_theory/MultiplicativeFunctions.py`の`MultiplicativePrefixSum.run`で、素数上の累積和と素数冪の値から乗法的関数の総和を求める。公開APIは変更していない。

## 実装

[公式のMin 25実装](https://github.com/yosupo06/library-checker-problems/blob/1814c4e5205517e368bb57a8d1127eb961cfeaae/number_theory/sum_of_multiplicative_function/sol/min_25_sieve.cpp)を参考に、既存の反復探索を修正した。

- 各状態で全素数を走査していた処理を、残りの上限の平方根で打ち切る。
- 子に続く分岐がない場合は、状態を積まずに素数の集計表から直接足す。
- 素数の1乗・2乗に対するcallbackの値を共有する。
- 法指定時は探索中の係数を法で減らす。法省略時の整数・Fraction計算も維持する。
- 再帰は使わない。

素数の集計表は`O(N^(3/4)/log(N+2))`回の算術演算。`run`は`O((D+1)(T+1))`時間で、Dは`x*最大素因数(x)≤N`を満たす2以上の整数の個数、Tはcallbackの1回の時間。探索も表作成と同じ計算量だとは保証していない。

## 公式全件と反復測定

公式revision `1814c4e5205517e368bb57a8d1127eb961cfeaae` の`sum_of_multiplicative_function`を30ケースすべて通過した。上限N=10¹¹、制限10秒。依存込みの単独コードをPyPyで実行し、公式checkerで照合した。オンライン提出は行っていない。

全件検証で遅かった3ケースを各5回、毎回新しいprocessで逐次実行した。PyPy 3.10.14 / 7.3.16、Ryzen 7 3700X、WSL Linux。起動・JIT・入出力・素数表作成を含む。

| ケース | 時間の中央値 | 最大RSS |
| --- | ---: | ---: |
| example_02 | 1.64秒 | 106248 KiB |
| max_03 | 1.67秒 | 106280 KiB |
| max_01 | 1.72秒 | 106272 KiB |

15回すべて公式checkerで通過。最大RSSは約104 MiBで、メモリ制限は強制していない。上限10¹³の`sum_of_multiplicative_function_large`は、後述の別検証で扱う。

- [公式全件の判定](../../verify/library_checker/results/sum_of_multiplicative_function.json)
- [各回の時間・RSS・入力とsourceのhash](../../verify/library_checker/benchmarks/sum_of_multiplicative_function.json)

## 以前の総和探索だけの比較

以前の探索改善時に、commit `ccc0335adba8522f9f66e0a351a6a5e1cd9d7c54`から`run`だけを取り出して比較した。下表の変更後はその測定時の実装を指す。関数は`f(p**e)=123*e+456*p`、法469762049で共通。素数の集計表を準備してから計測を始め、毎回新しいPyPy processで各5回、実行順を混ぜて測った。

| N | 変更前の中央値 | 変更後の中央値 |
| --- | ---: | ---: |
| 10⁸ | 1.739秒 | 0.0317秒 |
| 10⁹ | 25.045秒 | 0.0483秒 |

全回で新旧の答えが一致した。この表は総和探索部分だけで、素数表作成・起動・入出力を含まない。提出全体が同じ倍率で速くなるという意味ではない。C++上位提出との速度比較でもない。

[比較の各回の記録とsourceのhash](../../verify/library_checker/benchmarks/comparisons/multiplicative_sum.json)を保存している。

## 独立した正しさの検査

専用テストで、全整数の素因数分解から求めた値との照合、φ関数・約数関数、ランダムな素数冪の値、負値、法1・合成数の法、Fraction、N=0・1、素数冪境界、繰り返し呼出し、入力表の非破壊を検査する。Dirichlet積・除算・累積和復元のテストも同じファイルで検査する。

## 大きい上限での計算

`sum_of_multiplicative_function_large`のdriverも同じ`MultiplicativePrefixSum`を使う。上限は10¹³、制限は30秒。通常版の通過結果だけでlarge版を通過扱いにはしない。現在の判定は[large版の公式全件結果](../../verify/library_checker/results/sum_of_multiplicative_function_large.json)で確認できる。

採用版の公式20ケースは12件AC、8件TLE。TLEは`example_02`、`max_00`・`max_01`、`boundaryA_02`・`boundaryB_02`、`hack_wrong_zky_method_03`・`04`・`05`。全件通過には達していない。

- 個数の篩と法付き素数和の篩では、2を別に扱い、小さい値の表には奇数だけを保持する。
- 法付きの素数和は更新のたびに余りへ戻し、巨大整数の和を保持しない。
- 同じ探索状態から出る葉の寄与を足してから、共通の係数を1回だけ掛ける。
- 子を作る範囲と葉だけの範囲、表の参照方法が変わる範囲を分け、内側のループの分岐を減らす。

### 除算の正確性

[公式C++実装](https://github.com/yosupo06/library-checker-problems/blob/1814c4e5205517e368bb57a8d1127eb961cfeaae/number_theory/sum_of_multiplicative_function_large/sol/correct.cpp)も商の計算に浮動小数点除算を使う。この実装では、非負整数の被除数が2⁵⁰以下のときだけ`int(value / divisor)`を使い、範囲外では整数除算に戻す。

binary64で被除数・除数が正確に表現できる範囲では、除算の絶対誤差は、商の小数部分が整数境界まで離れている最小幅`1/divisor`より小さい。割り切れる場合の整数商は正確に表現できるため、切り捨てた結果は整数除算と一致する。除数が被除数より大きい場合の商は0。

剰余の計算には通常の`%`を使う。逆数から商を求めて整数で補正する案も試したが、PyPyでは速くならなかったため採用していない。

テストでは除算の閾値の前後、除数の倍数の前後、大きな法、乱数を整数演算と照合する。表の全商位置も独立した素数列挙と比較する。

### 最大公式入力での比較

[比較記録](../../verify/library_checker/benchmarks/comparisons/multiplicative_sum_large.json)では、commit `23457b9c61f00cd404df9fc1a1c95ebaacbb92d5`のclassと現在のclassを、同じ公式入力で各3回測る。各回で新しいPyPy processを使い、実行順を混ぜ、公式checkerで答えを照合する。時間・最大RSS・素数表作成と総和探索の内訳を残す。

公式`max_00`はN=10¹³、a=192279222、b=156648748。PyPy 3.10.14 / 7.3.16、Ryzen 7 3700X、WSL Linuxでの結果：

| 実装 | 全体の中央値 | 最大RSS |
| --- | ---: | ---: |
| 変更前 | 105.394秒 | 1005768 KiB |
| 採用版 | 39.450秒 | 415592 KiB |

全6回で公式checkerを通過。時間は約2.67倍速く、最大RSSは約59%減った。ただし採用版も30秒を超えるため、このケースは公式時間制限内の通過ではない。

採用版の段階別中央値は、素数個数8.765秒、素数和12.221秒、総和探索17.218秒。全体時間には構築・表の結合・起動・入出力・比較用の旧class読込も含む。探索だけを測った以前の比較とは直接比べない。

比較用の測定上限180秒と、公式判定の30秒は別。`checkerPassed`だけでは制限内通過を意味しない。`withinTimeLimit`と公式全件結果も確認する。

## 再実行

```sh
pypy3 -m pytest -q library_codex/verify/number_theory/test_multiplicative_functions.py
pypy3 library_codex/tools/check_library_checker.py test sum_of_multiplicative_function --official /path/to/library-checker-problems
pypy3 library_codex/benchmarks/official_benchmark.py sum_of_multiplicative_function --official /path/to/library-checker-problems --repeat 5 --slowest 3
pypy3 library_codex/benchmarks/multiplicative_sum_comparison.py
pypy3 library_codex/tools/check_library_checker.py test sum_of_multiplicative_function_large --official /path/to/library-checker-problems
pypy3 library_codex/benchmarks/multiplicative_sum_large_comparison.py --official /path/to/library-checker-problems --repeat 3
```
