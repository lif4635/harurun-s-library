# ライブラリ・サイト見直しメモ

更新日: 2026-08-10

この文書は、ライブラリとサイトを見ながら出た判断・疑問・後回し事項を、次の作業で失わないためのメモである。聞き取りが曖昧な名称は推測で確定せず、候補名と要確認事項を併記する。

## 今回決めたこと

### IntegerUtilities

2026-08-10に `algorithm/IntegerUtilities.py` を `integer_nth_root` だけへ整理した。

削除済み:

- `exact_square_root`
- `modular_power`
- `nearest_congruent_at_least`
- `decimal_digit_count`

実装ファイルと同時に、次も更新した。

- `number_theory/Elementary.py` と `algorithm/MiscAlgorithms.py` の import・再公開
- `modpow`、`SqrtInt`、`isDigit` などの旧名
- test
- API metadata、catalog、bundle、サイト

特別な理由がない互換 alias は残さない。

### FPS

FPS、Polynomial、Convolution の境界と、998244353 専用実装の構成は、別の回で丁寧に精査する。今回は勢いで統合・削除しない。

### Fenwick Tree

2026-08-10に `fenwick_tree/FenwickTree.py` / `FenwickTree` を
`fenwick_tree/BIT.py` / `BIT` へ変更した。互換aliasは設けず、内部依存、import、
bundle、説明、catalog、site dataを同じ変更単位で更新する。

## 説明を直す対象

### PermutationGroup

対象: `algorithm/PermutationGroup.py`

`simplify_permutation_subgroup(n, permutations)` は、単に置換を「簡単にする」関数ではない。入力された生成元と同じ置換群を表す、安定化列に沿った代表元の集まりを作る。

返り値 `levels` の意味:

- `levels[i]` は、`i + 1, ..., n - 1` を固定する部分群の中で、位置 `i` の移り先ごとに選んだ代表置換のリスト
- 各 level 内では、位置 `i` の移り先が重複しない
- 全 level の置換を合わせると、入力と同じ部分群を生成する
- 群の要素数は、各 level の長さの積から求められる

用途は、生成元で与えられた置換群の圧縮、群の位数計算、所属判定などの土台。
randomized testで元の生成元と同じ群を生成すること、各level長の積が群の位数になることを確認しているため保持する。
サイトにはlevelの意味と $S_3$ の例を掲載した。不要な `SimplifyPermutationSubgroup` aliasは2026-08-10に削除した。

### Search

対象: `algorithm/Search.py`

#### binary_search_int / binary_search_float

一般的な `[left, right)` を直接受け取る API ではない。`predicate(false_value) == False` と `predicate(true_value) == True` が既知である二点を渡し、その境界を探す。昇順・降順のどちら向きの二点でも動く。この前提を signature の近くへ明記する。

#### kth_element

発言中の「QELEMENT」は `kth_element`、「新フラ」は C++ の `std::nth_element` を指す可能性が高い。

2026-08-10にintroselect型へ改善した現在の実装:

- 入力をコピーするため、呼び出し元の list は並べ替えない
- 先頭・中央・末尾のmedianをpivotにする
- pivot 未満、同値、超過の三分割を行う quickselect
- `index` は 0 始まりで、`index` 番目に小さい値を返す
- 平均線形時間。分割が偏り続けた場合はsortへ切り替え、最悪 $O(N\log N)$

20万要素のPyPy実測では、random列で`sorted`の約6.2倍、重複が多い列で約3.5倍高速だった。
整列済み・逆順ではPython組み込みsortの方が速いが、現在の早期判定でも1〜2ms程度であり、選択APIとして保持する。

### 区間

#### RangeSet

対象: `ordered_set/RangeSet.py`

この module の区間はすべて半開区間 `[left, right)` とする。

- `add(left, right)`: `[left, right)` を追加し、新しく集合に加わった整数の個数を返す。重なる区間と隣接区間は結合する
- `discard(left, right)`: `[left, right)` を削除し、実際に集合から消えた整数の個数を返す
- `contains(value)`: 一点 `value` が集合に含まれるかを返す
- `mex(value=0)`: `value` 以上で集合に含まれない最小の整数を返す
- `intervals()`: 集合を表す、互いに交わらない半開区間を左端順で返す

「区間リスト」だけでは開閉が分からないため、module 冒頭、引数、返り値のすべてで `[left, right)` を見えるようにする。具体例も追加する。

#### merge_intervals

対象: `algorithm/SequenceAlgorithms.py`

こちらも半開区間 `[left, right)` として説明する。`merge_adjacent=True` なら `[a, b)` と `[b, c)` も結合する。引数 `merge_adjacent` の説明を具体化する。

## Convolution・Polynomial・FPS の境界

サイトでは次の役割を明確に分ける。

- Convolution: 係数列同士の積を計算する基礎処理
- Polynomial: 有限次数の多項式として、除算、剰余、補間、多点評価などを扱う
- FPS998: mod 998244353 上の形式的冪級数として、指定次数で打ち切った inverse、log、exp、pow、composition などを扱う

### MiddleProduct

対象: `convolution/MiddleProduct.py`

2026-08-10に標準的なmiddle productへ置き換えた。現在は、長さnの列aと長さmの列bに対し、`c[i] = sum(b[j] * a[i+j])` を長さn-m+1で返す。

998244353では、長さn以上の最小2冪による循環NTTを使う。不要な係数が返す範囲へ巡回しないことを利用し、全畳み込みに必要な長さより小さい変換で済ませる。PyPy、n=131072、m=65536の計測では、専用実装38.1ms、全畳み込み後の切り出し81.2msだった。

発言中の「real product」はこの module を指している可能性が高いが、要確認。

### MultipointEvaluation

対象: `polynomial/MultipointEvaluation.py`

`multipoint_evaluation(f, points)` は、係数列 `f` が表す一つの多項式を、`points` の各点で評価し、その値を入力順の list で返す。Convolution そのものではなく、内部で高速な多項式積を利用する Polynomial の処理。

`polynomial_interpolation` は、点と値の組から、その全点を通る多項式の係数列を復元する。点評価と補間を同じ page に置くなら、互いに逆方向の処理だと冒頭で説明する。

FPS 全体の本格的な再整理は後回しにするが、この三分類だけは先にサイトのカテゴリ説明へ出す。

## サイト共通の問題

### 計算量

生成済み API 文書には「各操作の計算量はAPI表を参照」が155 pageにあり、関数・method表にも計算量欄がなかった。

2026-08-10に生成処理を修正し、この文言は0件になった。function・constructor・methodごとの計算量を表へ追加し、metadataまたはsource docstringに根拠がない項目はダッシュ表示にして、moduleの計算量を無理に流用しない。

直し方:

- function / method ごとに Complexity を表示する
- module 全体に一つの曖昧な計算量を書かない
- API 表を参照させる文だけを置かない
- 根拠のない複雑度を自動生成しない。分からない場合は空欄にして要整備として検出する
- `tools/build_api_reference.py` の fallback 文言から直し、再生成後にも戻らないようにする

2026-08-10の追加監査で、公開function・methodの「実装依存」を0件にした。
callableを受け取るAPIは、全体のBig-Oだけでなく `op`、`compare`、`cost`、
`transitions`、`options` などを何回呼ぶかを書く。`M(N)`、`alpha(N)`、`B` のような
記号は、同じ計算量欄で意味も説明する。

計算量を埋める過程で標準的な実装より不必要に遅いと判明した場合は、説明だけで
済ませず、正しさをtestした上で改善する。2026-08-10には次を改善した。

- `integer_nth_root`: 値域の二分探索から整数Newton法へ変更
- `SurrealNumber.larger/smaller/between`: 数直線を1ずつ歩く処理をdyadic有理数の直接計算へ変更
- `QBinomial` constructor: q整数を毎回再計算する二乗時間前計算を線形時間へ変更

2026-08-10の追加高速化では次も改善した。

- `polynomial_gcd` / `polynomial_extended_gcd`: 大次数をHalf-GCD法へ変更。小次数は従来Euclid法を使うhybridで、計算量は $O(M(N)\log N)$
- `polynomial_resultant`: Half-GCDが生成するEuclid商の列から次数・最高次係数を復元し、$O(M(N)\log N)$ で計算
- `PolynomialFactorization` / `polynomial_inverse_mod`: 上記GCD・拡張GCDを内部利用するため同時に高速化
- `SortableSegmentTree`: 平方分割からsegment treeへ変更し、`update` / `query`を $O(\log N)$ に改善。range sortはPython組み込みsortを維持
- `LazyKDTree` constructor: 各部分木の再sortをやめ、x/yの事前sort列をlevelごとにpartitionして $O(N\log N)$ 構築へ変更

PyPyでの比較では、多項式GCD+resultantは4096次で約1.2倍、8192次で約2.4〜2.6倍、`SortableSegmentTree`のupdate/query混合workloadは10万操作で約2倍、20万操作で約2.9倍だった。性能検査は従来法とのchecksum一致も確認する。

### iPhone の「ホーム画面に追加」アイコン

site source には次の asset が既にある。

- `apple-touch-icon.png` (180 x 180)
- `icon-192.png`
- `icon-512.png`
- `site.webmanifest`

2026-08-10に正規の猫画像を新しい`yura-touch-icon.png`へ複製し、HTMLの`apple-touch-icon`とmanifestの180px iconをこのURLへ切り替えた。
manifestには`id`・`scope`・各iconの`purpose: any`も明示した。以前のURLを掴んだiOS cacheを避けつつ、旧URLも既存端末用に残す。

## 2026-08-10の残件解消

- `Comb`の階乗・逆階乗を正規名`F(n)`・`Fi(n)`で呼べるようにし、冗長な`fact`は削除した。
- catalog全体の返り値説明を監査し、曖昧なpurpose・return・tuple説明52件を0件にした。
- description auditを通常検査へ組み込み、今後同じ曖昧説明が追加された場合は検査を失敗させる。
- quick性能回帰9系統を再計測し、全て基準を通過した。`kth_element`も入力傾向別に再計測した。
- Convolution / Polynomial / FPS998のカテゴリ分離、FPS998の旧機能範囲・Library Checker上位実装との演算別比較は完了済み。
- iPhone用iconをcache更新可能な専用URLへ移した。

意図的に保留しているのは`REFERENCE_INVENTORY.md`で`[~]`とした高度なGeometry 22件だけである。
各変更は今後もtest、catalog、bundle、サイトを同期できる単位で行う。
