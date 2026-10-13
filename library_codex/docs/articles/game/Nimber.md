# Nimの積・逆元

## 主な機能

64bit以下の非負整数をnimberとして扱い、nim積を計算する。通常の整数積ではなく、たとえば2と2のnim積は3になる。問題でnim積が定義されているときや、加算をXORとする体上の計算に使う。通常のNimの山を合わせるだけならXORで足り、nim積は必要ない。

- `nim_product64(a, b)`: 64bitのnim積を整数で返す。積だけ必要ならこれを使う。
- `nim_product16(a, b)`・`nim_product32(a, b)`: 入力の上限が16bit・32bitと分かっている場合に使う。
- `Nimber(value, bits=64)`: 加減算・積・除算を演算子で書き、`power`で累乗、`inverse`で逆元を求める。
- `NimberToField(root)`: rootの累乗を基底とする多項式表示との変換を行う。単に積を求める場合は不要。

64bit版は初回の非自明な積でO(2^16)時間・領域の表を作り、その後は1回O(1)。16bit・32bitだけを使う場合、この追加の表は作らない。別途、moduleの読み込み時にO(2^16)の8bit積表を作る。

## 使い方

```python
assert nim_product64(2, 2) == 3
assert nim_product64(2, 3) == 1
assert nim_product64(0, 12345) == 0

a = Nimber(2)
b = Nimber(3)
assert int(a + b) == (2 ^ 3)
assert int(a * b) == 1
assert int(a * a.inverse()) == 1
assert int(a.power(2)) == 3
```

- 関数の返り値は整数。入力が64bit以内なら、結果も64bit以内。
- `Nimber`の演算結果は同じbit幅の`Nimber`。整数を取り出すときは `int(...)`。
- 加算・減算はどちらもXOR。積を通常の整数積や「整数積を2の冪で割った余り」で代用できない。

## 仕組み

16bitの非零nimberは、ある生成元の累乗で表せる。指数から値、値から指数の表を用意すると、16bitの積を指数の加算と表引きで求められる。

64bitの積は16bitの部分へ分解する。小さい積を9回求め、固定値との積は別の表で処理する。毎回8bitまで細かく分解していた処理を減らしている。

## 注意点

- `nim_product16`・`32`・`64`へ渡す値は、指定bit幅以内の非負整数。範囲検査は行わない。
- `Nimber`のbit幅は8・16・32・64。異なる幅同士の演算はできない。
- 0の逆元は存在せず、`inverse()`は`ZeroDivisionError`を送出する。
- `power(exponent)`は非負の指数のみ。計算量はO(log(exponent+1))回の積。
- `NimberToField`は、渡したrootの累乗が基底にならなければ`ValueError`を送出する。
