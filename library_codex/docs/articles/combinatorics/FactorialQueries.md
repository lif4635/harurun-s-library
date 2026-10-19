# 離れた添字の階乗をまとめて求める

`factorials(indices)`は、複数の非負整数の階乗を998244353で割った余りを、入力と同じ順番で返す。添字が法に近い場合も、そこまでの階乗表は作らない。

## 主な機能

- `factorials(indices)` — 離れた添字や重複を含む問い合わせを一括処理するfunction。入力はlistでもiteratorでもよい。
- 法以上の添字には0を返す。負の添字には`ValueError`を送出する。
- 小さい添字の階乗や二項係数を繰り返し求める用途には、前計算を保持する`Combination`を使う。このfunctionは呼び出しごとに計算し、状態を保持しない。

返り値の各要素は次の値。

$$
\mathrm{result}[i]=\mathrm{indices}[i]!\bmod 998244353.
$$

## 使い方

```python
from library_codex.combinatorics.FactorialQueries import factorials

values = factorials([5, 0, 10, 5, 998244352, 998244353])
print(values)
```

出力は`[120, 1, 3628800, 120, 998244352, 0]`。

- listの長さは問い合わせ数と同じ。
- 並び順と重複は入力のまま。入力をソートしたり変更したりしない。
- 空の入力には空listを返す。

## 仕組み

法の後半の添字は、Wilsonの定理で前半へ移す。

$$
n!\,(p-1-n)!\equiv(-1)^{n+1}\pmod p,
\qquad p=998244353.
$$

移した後の最大添字をAとする。Aが262144以下なら、問い合わせを並べ替えて一度だけ順に掛ける。大きければ、幅B=1024ごとの積を多項式の等間隔評価とNTTでまとめて作る。各問い合わせでは、最寄りの区切りから端数だけを掛ける。同じ区切り内の問い合わせは途中結果を再利用する。

問い合わせ数をQ、`K=max(B, floor(A/B))`とすると、大きい場合は`O(K log(K+2) + Q log(Q+2) + min(A, Q B))`時間、`O(K+Q)`メモリ。小さい場合は`O(A+Q log(Q+2))`時間、`O(Q)`メモリ。法での整数演算を定数時間とする。

## 注意点

- 法は998244353固定。任意の素数の法で少数の階乗を求める場合は`LargePrimeFactorial`を使う。
- 返り値は階乗の正確な巨大整数ではなく、法で割った余り。
- 問い合わせをまとめて渡す。1件ずつ呼ぶと多項式の前計算を共有できない。

## 参考

- [Library Checker Many Factorials](https://judge.yosupo.jp/problem/many_factorials)
- [公式解の区切りごとの階乗前計算](https://github.com/yosupo06/library-checker-problems/blob/1814c4e5205517e368bb57a8d1127eb961cfeaae/enumerative_combinatorics/many_factorials/sol/correct_log_time_multieval_faster.cpp)
