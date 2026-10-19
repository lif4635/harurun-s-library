# 巨大整数の除算

10進・16進の文字列から商と余りを求め、同じ進数の文字列で返す。負数を含め、Pythonの`divmod`と同じ切り下げ除算を行う。

## 主な機能

- `divide_decimal`と`divide_hex`は文字列を受け取り、商と余りも同じ進数の文字列で返す。
- 巨大な10進文字列を分割して処理するため、Pythonの整数文字列変換の上限設定を変えずに使える。
- Nを2入力の合計bit数、D(N)を標準の整数除算時間、M(N)を整数乗算時間とする。16進版はO(D(N)+N)時間、10進版はO((D(N)+M(N)+N) log(N+1))時間が上界。追加領域はO(N) bit。
- すでに`int`になっている入力には、標準の`divmod`を使う。

## 使い方

```python
from library_codex.number_theory.BigIntegerDivision import divide_decimal, divide_hex

q, r = divide_decimal("-17", "5")
decimal = divide_decimal("100000000000000000001", "3")
hexadecimal = divide_hex("ff", "10")
```

- `q`は`"-4"`、`r`は`"3"`。商を0方向へ丸めた`"-3"`ではない。
- `decimal`は`("33333333333333333333", "2")`。
- `hexadecimal`は`("F", "F")`。16進の返り値は大文字。

商qと余りrは次の関係を満たす。

$$
A=qB+r,\qquad q=\left\lfloor\frac{A}{B}\right\rfloor.
$$

- Bが正なら、余りは0以上B未満。
- Bが負なら、余りはBより大きく0以下。たとえば`divide_decimal("17", "-5")`は`("-4", "-3")`。

## 仕組み

整数の除算には標準の`divmod`を使う。PyPyで比較した公式入力では、自前の逆数近似方式より速かった。16進は文字列との変換も標準機能で処理する。

10進の入力は512桁ずつ読み、平衡な順序で結合する。出力は10の冪で二分する。この除算は2の冪によるbitシフトと5の冪による除算に分ける。全桁を一度に`int`や`str`へ渡さず、再帰も使わない。浮動小数点や外部packageは不要。

## 注意点

- 除数が0なら`ZeroDivisionError`。
- 文字列はASCII数字と先頭の`+`・`-`だけを許す。16進は`a`〜`f`・`A`〜`F`も使える。先頭0は許す。
- 空白、`_`、`0x`、全角数字、空文字列は`ValueError`。
- 出力には先頭の余分な0や`+`を付けない。ゼロは`"0"`。
- 10進200万桁・16進160万桁を含むLibrary Checker公式ケースでPyPy検証を行う。測定条件と結果は[比較記録](https://github.com/lif4635/harurun-s-library/blob/main/library_codex/docs/BIG_INTEGER_DIVISION_BENCHMARK.md)にまとめる。
