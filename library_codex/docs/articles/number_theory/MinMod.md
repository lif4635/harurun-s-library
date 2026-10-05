# 一次式の剰余の最小値

## 主な機能

`min_mod(n, modulus, multiplier, addend)`は、整数`i`を半開区間`[0, n)`で動かしたときの最小の余りを返す。

$$\min_{0\le i<n} (\mathrm{multiplier}\cdot i+\mathrm{addend})\bmod\mathrm{modulus}$$

全項を列挙せず、除算で範囲を縮める。整数演算を定数時間として`O(log modulus)`時間、追加領域`O(1)`。

## 使い方

```python
from library_codex.number_theory.MinMod import min_mod

answer = min_mod(4, 13, 5, 7)
assert answer == 4
```

余りの列は`[7, 12, 4, 9]`で、返るのは最小値`4`。最小値を取る添字は返さない。

## 仕組み

余りが折り返す直前までの区間では値が増えるので、折り返し直後だけを候補に残す。この候補列も一次式の剰余で表せる。必要なら列を逆順に見て、各反復で法を半分以下へ縮める。

## 注意点

- `n`と`modulus`は正の整数。空の範囲は指定しない。
- `multiplier`と`addend`は負でもよい。内部で法により正規化する。
- 返り値は`0`以上`modulus`未満。
