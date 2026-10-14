# 小さい素数を法とするStirling数

添字が大きく、通常のDPでn行目まで表を作れないときに使う。法pが小さい素数なら、p未満の表だけでnが10の18乗程度の問い合わせにも答えられる。

## 主な機能

`query = StirlingNumberQuery(p)`を作り、`query.first_kind(n, k)`で符号付き第一種、`query.second_kind(n, k)`で第二種を取得する。

- 第二種は、区別できるn個の要素をk個の空でないグループへ分ける個数。グループの順序は区別しない。
- 符号付き第一種は、下降階乗を展開したときの係数。符号なし第一種とは異なる。

$$
x(x-1)\cdots(x-n+1)=\sum_{k=0}^{n}s(n,k)x^k
$$

構築は時間・領域ともに`O(p)`。各種類の表が初めて必要になったときに、その種類の表を`O(p²)`時間・領域で作る。以降の問い合わせは`O(1 + log_p(n+1))`時間、追加領域`O(1)`。整数の四則演算を定数時間として数える。

使った種類の三角表だけを保持し、各値を16ビットで保存する。p=4999なら1種類の表の要素部分は約25 MB。これとは別に配列管理や実行環境のメモリを使う。

## 使い方

```python
from library_codex.combinatorics.StirlingNumberQuery import StirlingNumberQuery

query = StirlingNumberQuery(7)
assert query.second_kind(5, 2) == 1
assert query.second_kind(5, 3) == 4

assert query.first_kind(5, 2) == 6
assert query.first_kind(5, 3) == 0

assert query.second_kind(0, 0) == 1
assert query.second_kind(5, 0) == 0
assert query.second_kind(5, 6) == 0
```

第二種では5個を2組へ分ける方法が15通りなので、7で割った余りの1を返す。第一種の5次の下降階乗は次のようになり、2次の係数は-50なので、7で割った余りの6を返す。

$$
x(x-1)(x-2)(x-3)(x-4)=x^5-10x^4+35x^3-50x^2+24x
$$

返り値は次のとおり。

- `int`。常に0以上p未満の剰余。
- `n == k == 0`なら1。
- `n < 0`、`k < 0`、`k > n`、または`n > 0`かつ`k == 0`なら0。

## 仕組み

p未満の値はStirling数の漸化式で前計算する。大きな添字の値は、小さい表の1要素と二項係数の積へ縮約する。二項係数は階乗・逆階乗表とLucasの定理で計算するため、二項係数用の二次元表は作らない。

第一種では、素数p上での次の恒等式を使う。

$$
(x)_{ip+j}=(x^p-x)^i(x)_j,\qquad 0\le j<p
$$

## 注意点

- pは2以上65535以下の素数。合成数や範囲外の値は`ValueError`。
- 上限までの構築が軽いという意味ではない。前計算が二次なので、実用上は数千程度のpを想定する。998244353のような大きな法には使えない。
- n・kは整数。
- 第一種で符号なしの個数が必要なら、n−kが奇数のときだけ返り値の符号を反転してpで剰余を取る。
- 第一種と第二種の両方を使うと、それぞれの表のメモリが必要になる。

## 参考

[maspy: Stirling 数を p で割った余りの計算](https://maspypy.com/stirling-%E6%95%B0%E3%82%92-p-%E3%81%A7%E5%89%B2%E3%81%A3%E3%81%9F%E4%BD%99%E3%82%8A%E3%81%AE%E8%A8%88%E7%AE%97)
