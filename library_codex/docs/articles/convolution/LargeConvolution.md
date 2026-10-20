# NTTの長さ上限を超える畳み込み

2つの多項式の積を、係数の法998244353で求める。出力が2^23項を超えても計算できる。

## 主な機能

- `multiply(first, second)` — 昇べき順の係数列を受け取り、積の全係数を返す。片方が空なら空list。
- 通常サイズでは`NTT998.multiply`を使う。大きい場合は入力を分割し、各ブロックの順NTTを一度ずつ計算する。
- 同じlistを両方へ渡す二乗では、入力の順NTTを共有する。
- 片方だけ短い場合は、その変換を保持し、長い方を1ブロックずつ処理する。

## 使い方

```python
from library_codex.convolution.LargeConvolution import multiply

c = multiply([1, 2, 3], [4, 5])
print(c)
```

`[4, 13, 22, 15]`を返す。`c[k]`は積の次数kの係数で、入力は変更しない。負数や998244353以上の係数も余りへ直して計算する。

## 仕組み

ブロック長をB、各入力のブロック数をP、Qとする。同じ次数へ寄与するブロックの積をNTT後の配列で足し合わせ、出力ブロックごとに逆変換する。

時間は`O((P+Q) B log B + P Q B)`、追加メモリは`O((P+Q) B)`。Bは短い入力を覆う2の冪と2^22の小さい方を選ぶ。通常サイズの経路は`O((N+M) log(N+M))`、片方が60項以下なら`O(NM)`。

両方が長く、出力長を切り上げた2の冪が2^25のときは、添字を4で割った余りごとの4列へ分ける方式も使う。各列を長さ2^23でNTTし、各評価点で3次以下の多項式を掛ける。逆NTTは4回で済み、時間は`O((N+M) log(N+M))`、追加メモリは`O(N+M)`。ブロック分割で必要な変換回数が多い場合だけ、この方式を選ぶ。

## 注意点

- 出力は長さ`len(first)+len(second)-1`のlist。末尾の0も省略しない。
- 長さ上限を超えられることと、時間・メモリ制限に収まることは別。数千万項では入力・出力だけでも大きくなる。
- Library Checkerの最大ケースはPyPyで公式10秒制限に未達。[測定範囲と時間](https://github.com/lif4635/harurun-s-library/blob/main/library_codex/docs/LARGE_CONVOLUTION_BENCHMARK.md)を確認して使う。
- 各ブロックの変換結果は32bit整数配列で保持する。入力と返り値まで含めたピークメモリは、項数とPython処理系に依存する。

## 参考

[Library Checker公式の大規模畳み込み](https://github.com/yosupo06/library-checker-problems/tree/master/convolution/convolution_mod_large)
