# q二項係数

## 主な機能

固定した`q`と素数`mod`に対して、q二項係数を繰り返し求める。二項係数をqで重み付けした量で、次の漸化式で定義する。

$$\binom{n}{k}_q=\binom{n-1}{k}_q+q^{n-k}\binom{n-1}{k-1}_q$$

両端は1、範囲外は0。`q=1`なら通常の二項係数になり、`q=0`なら有効なすべての組で1になる。

`QBinomial(q, maximum, mod)`で表を作り、`C(n, k)`で剰余を取得する。`maximum < mod`なら構築O(maximum + log mod)時間・O(maximum)領域、表の範囲内の問い合わせはO(1)。途中でq階乗が0になる場合も、通常の二項係数との積へ分けて計算できる。

## 使い方

```python
from library_codex.combinatorics.QBinomial import QBinomial

table = QBinomial(2, 100, 998244353)
assert table.C(3, 1) == 7
assert table.C(3, 2) == 7
assert table.C(3, 4) == 0

table = QBinomial(-1, 100, 998244353)
assert table.C(4, 2) == 2
```

返り値は`0`以上`mod`未満の整数。整数として巨大な二項係数を作ってから余りを取る処理は行わない。

## 注意点

- `mod`には素数を指定する。素数判定は行わない。
- `maximum`は前計算するnの上限。0以上。負の`q`も法で正規化する。
- `maximum >= mod`にも対応する。この場合、通常の二項係数へLucasの定理を適用するため、問い合わせはO(log_mod(n+1))時間になる。
- 準備中にq階乗が0になる周期が見つかった場合は、上限外のnも計算できる。ただし表にない通常二項係数の桁は積で求めるので、選ぶ個数に比例して遅くなる。
- 周期が見つかっておらず、nが準備済みの表を超えた場合は`ValueError`。従来の仮の周期による誤計算を避けるため、明示的に拒否する。
- `q=0`では表を作らず、nの大きさにかかわらずO(1)で返す。
