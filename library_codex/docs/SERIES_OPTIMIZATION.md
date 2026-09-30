# 疎FPS・2変数FPS・SPSの調査

2026-09-30。対象は純粋なPython/PyPy。今回採用した変更と、調査のみの候補を分ける。公開APIは変更していない。サイトへの公開は未実施。

## 採用した変更

### 疎な1変数FPS

`fps998/FPS.py`には、非零項数が少ない場合の逆数・除算・log・exp・冪・平方根の自動切替がすでにある。いずれも疎な漸化式を使う経路は O(NK)。Nは出力長、Kは入力の非零項数で、結果が密になること自体は問題ない。

一方、専用の`fps/SparseFormalPowerSeries.py`の冪は、logを計算してからexpへ渡していた。logの結果が密になると、後段が O(N²) になる。負の指数も先に密な逆数を作っていた。

[Nyaanの疎FPS](https://nyaannyaan.github.io/library/fps/sparse-fps.hpp)で使われているのと同じ微分恒等式から、入力の非零項だけを使う反復へ変更した。g=f^eとすると、

$$
f g'=e f'g,
\qquad
g_n=\frac{1}{n f_0}\sum_{i=1}^{n}\bigl((e+1)i-n\bigr)f_i g_{n-i}.
$$

- 定数項が0の場合は先頭の次数を取り出し、最後に結果をずらす。
- 負の指数も、定数項が可逆なら同じ漸化式で求める。
- exp・logの各係数で逆元を求め直さず、階乗の逆元1回と逆向きの走査で逆数表を作る。必要な整数が可逆なら合成数の法でも動く。
- 不要な汎用FPS importを削除し、専用moduleのstandalone codeはNTTなどを含まない。
- degree=0の0乗が`[1]`を返していた不整合と、負のdegreeの検査漏れを修正した。

998専用版では、expの微分係数と冪の固定係数を前計算した。logは微分した結果を保持して除算する形にし、内側のループでの三因子の積を避けた。計算量や疎・密の切替閾値は変えていない。平方根の疎な経路も冪の内部処理を共有する。

### 集合冪級数

[hosのSetMul](https://github.com/hos-lyric/libra/blob/master/algebra/set_power_series.cpp)の次数範囲を参考に、`SubsetConvolution.multiply`で不要な次数の積を省いた。

maskの要素数をp、集合全体の要素数をnとすると、次数付きzeta変換後に積を計算する範囲は次だけでよい。

$$
p\leq k\leq\min(2p,n).
$$

下限未満は最終的な係数にも、その係数を求めるMobius変換にも使われない。上限を超える係数は0。計算量は O(n²2^n) のままで、exp・合成・power projectionにも共通の乗算の改善が効く。hos版の再帰構造自体は移植せず、既存の反復実装を維持した。

## 測定

WSL2、PyPy 3.10.14 / 7.3.16。同じ入力を新しいprocessで3回ずつ、旧版・新版の実行順を交互にして測った中央値。関数呼出し時間のみで、import・入力生成・JSON出力は含まない。ウォームアップなし。比較が完走したケースは結果全体のhashが一致。旧版は変更直前のsourceをrepository外の比較cacheへ保存したもの。C++との実行時間比較ではない。

疎な入力は定数項以外の非零項8個。1次の項と、残り7個を固定seedで選んだ次数へ配置した。値と非零項の位置によって時間は変わる。

| 演算 | サイズ | 変更前 | 変更後 |
| --- | ---: | ---: | ---: |
| 専用sparse_power | 16384 | 4.792秒 | 0.00983秒 |
| 専用sparse_power | 131072 | 10秒で打切り | 0.0252秒 |
| 専用sparse_exponential | 131072 | 0.0761秒 | 0.0201秒 |
| 専用sparse_logarithm | 131072 | 0.0621秒 | 0.0319秒 |
| 998専用fps_pow | 131072 | 0.0507秒 | 0.0234秒 |
| 998専用fps_exp | 131072 | 0.0407秒 | 0.0173秒 |
| 998専用fps_log | 131072 | 0.0462秒 | 0.0248秒 |
| 部分集合畳み込み | 18要素、262144係数 | 1.459秒 | 0.976秒 |
| SPS exp | 同上 | 1.074秒 | 0.775秒 |
| SPS合成 | 同上 | 1.788秒 | 1.431秒 |

131072の旧sparse_powerは完走していないため、そこでの旧版との結果一致や確定した速度比は主張しない。大きな入力の正解は別途、(1-x)^(-2)の既知係数と照合した。

最大RSSも測定した。998専用logは87.2MiB→90.4MiBで約3.3MiB増えた。微分係数と返却用配列を別に持つためで、時間短縮との交換になる。SPS乗算は162.6MiB→161.3MiB、expは127.0MiB→127.3MiB、合成は149.7MiB→150.0MiBで、大きな追加メモリは見られなかった。

生データは`benchmarks/results/library_checker/`の`sparse-*.json`、`fps998-sparse-*.json`、`sps-*.json`。各回の時間・最大RSS・入出力hash・比較source hashを記録した。SPSの18要素は今回の測定サイズであり、Library Checkerの最大入力をすべて比較したという意味ではない。

```sh
pypy3 library_codex/benchmarks/compare_sparse_fps.py --baseline ../lc-comparison/sparse-before.py --operation power --size 131072 --timeout 10 --output library_codex/benchmarks/results/library_checker/sparse-power-131072.json
pypy3 library_codex/benchmarks/compare_sparse_fps.py --baseline ../lc-comparison/fps998-before-sparse.py --candidate library_codex/fps998/FPS.py --operation power --output library_codex/benchmarks/results/library_checker/fps998-sparse-power.json
pypy3 library_codex/benchmarks/compare_set_series.py --baseline ../lc-comparison/set-function-before.py --bits 18 --operation compose_egf --output library_codex/benchmarks/results/library_checker/sps-compose-18.json
```

## 2変数FPSの最初の整備

`fps998/NTT2D.py`は2次元NTT・畳み込みを担当し、`fps/MultivariateFPS.py`は各変数の次数を打ち切る逆数・log・exp・整数冪を担当する。最初の整備では後者と共通の`convolution/MultivariateMultiplication.py`を改善した。以下はその時点の変更記録で、後続比較を踏まえた現行実装は「2変数FPSの本体への採用」に記載する。新しい互換aliasは追加していない。

- [Nyaanの多変数FPS](https://nyaannyaan.github.io/library/fps/multivariate-fps.hpp)を参考に、逆数とexpの計算精度を1,2,4,...と倍増するように変更。各段で全サイズを計算していた無駄をなくした。変換済み配列の使い回しは後続比較を経て採用した。
- 2変数の積は、x方向の行幅Wに対して間隔2W−1で係数を並べ、998専用の1次元畳み込みへ渡す。これによりxの次数の繰り上がりがyの係数へ混ざらない。長方形を正方形へ膨らませない。998の変換長上限を超える場合は従来の色分けNTTへ戻す。
- 疎な2変数の逆数・log・exp・定数項非0の整数冪を追加。入力の非定数・非零項Kが16以下、法998244353のときO(N*(K+1))の漸化式を使う。出力が密になる場合も入力の非零項だけで計算する。
- [maspypyの疎な2変数冪](https://github.com/maspypy/library/blob/main/poly/2d/fps_pow_1_2d.hpp)と同じ関係f*Dg=e*(Df)*gから冪を計算する。ただし、実装は行単位の偏微分ではなく、平坦化した位置を重みとするEuler微分を使う。
- 定数項非0・998244353で絶対値8を超える指数は、正規化してlogとexpから計算する。小さな指数や定数項0は二分累乗を使う。負の冪の再帰呼出しも不要にした。
- 1からN−1までの逆数表は逆元1回と前後の走査で生成する。log・exp・積分にはこれらの整数が可逆であることが必要。

2変数の密な積・逆数・log・expはO(N log(N+1))時間・O(N)領域。N=W*H。矩形の次数制限であり、総次数の制限ではない。平坦な係数列の順序と例は[利用記事](articles/fps/MultivariateFPS.md)に記載した。既存のderivativeは通常の偏微分ではないことも明記した。

[maspypyの2変数逆数](https://github.com/maspypy/library/blob/main/poly/2d/fps_inv_2d.hpp)のような行方向の変換結果の再利用も、後述の比較用試作で測定した。本体への採用や、C++上位実装と全演算の比較完了を意味しない。

### 2変数の測定方法

PyPy、同一入力、新規process、ウォームアップなしで3回ずつ測る。旧版は2つの変更対象moduleを変更前に固定し、乗算も旧版を呼ぶようにして比較した。入出力hash、source hash、時間、最大RSSは`benchmarks/results/library_checker/bivariate-*.json`に保存する。密な入力は全係数を固定seedで選び、疎な入力は定数項以外のランダムな8位置を非零にする。疎な結果が全係数非零とは限らない。冪の指数は1234567。

```sh
pypy3 library_codex/benchmarks/compare_multivariate_fps.py --baseline ../lc-comparison/multivariate-fps-before.py --baseline-multiply ../lc-comparison/multivariate-multiply-before.py --operation exponential --width 16 --height 4096 --output library_codex/benchmarks/results/library_checker/bivariate-exp-tall.json
```

比較用の旧sourceはrepository外のcache。再現時は`--baseline`と`--baseline-multiply`へJSON記録とhashが一致する旧sourceを指定する。異なるsourceとの比較は別の比較結果として扱う。

### 2変数の測定結果

全て65536係数。時間は3回の中央値。全ケースが完走し、旧版・新版の出力全体のhashが一致した。

| 演算 | 形 W×H | 入力 | 変更前 | 変更後 |
| --- | --- | --- | ---: | ---: |
| 逆数 | 256×256 | 密 | 1.483秒 | 0.337秒 |
| 逆数 | 16×4096 | 密 | 2.069秒 | 0.334秒 |
| 逆数 | 4096×16 | 密 | 2.142秒 | 0.315秒 |
| exp | 256×256 | 密 | 14.636秒 | 0.908秒 |
| exp | 16×4096 | 密 | 29.503秒 | 0.850秒 |
| exp | 4096×16 | 密 | 31.753秒 | 0.804秒 |
| 整数冪 | 256×256 | 密 | 2.673秒 | 1.214秒 |
| log | 256×256 | 疎・K=8 | 1.297秒 | 0.0202秒 |
| exp | 256×256 | 疎・K=8 | 12.203秒 | 0.0204秒 |
| 整数冪 | 256×256 | 疎・K=8 | 2.170秒 | 0.0212秒 |

各processの最大RSSについて3試行中の最大を比較すると、正方形の逆数は105.6→99.8MiB、expは113.9→112.4MiB。長方形のexpは16×4096で118.3→113.2MiB、4096×16で118.1→109.2MiBだった。一方、密な整数冪は102.8→111.3MiBで約8.6MiB増えた。速度短縮と引き換えにlogとexpの中間配列を使うため。疎な3演算は変更後いずれも約79.7MiBだった。

これらはPyPy上で変更前後を比較した値であり、C++との速度比や最大サイズ全域での優劣を表すものではない。

## 2変数FPS: 手法とC++参照実装の比較

2026-09-30の比較段階の記録。この段階では比較用コード・テスト・測定記録だけを追加し、本体は変更していない。表のcurrentは採用前の実装であり、後述の採用後の値と区別する。

### 比較対象

| 記録中の名前 | 実装 |
| --- | --- |
| current | 現在のPyPy版。係数を間隔付きで詰める積と精度倍増。非零項16個以下は疎な漸化式 |
| colored | Nyaanを参考にした2色NTTの逆数。Newton更新の中で逆数側の変換を再利用 |
| row | maspypyを参考にした行ごとのNTTを保存する逆数。列方向の変換を組み合わせる |
| sparse | 疎な漸化式の16項制限を外し、ループ内の固定係数も前計算する試作 |
| maspy | maspypyのC++版2変数inv・log・exp。冪は定数項1の入力にexp(e log f)を使う比較用adapter |
| nyaan | NyaanのC++版多変数FPSを2変数で使用 |

colored・rowは**逆数の内部処理だけを置き換えた試作**。log・exp・冪の外側の積は現行版のままで、各作者のC++版全体をPythonへ移植したものではない。疎な経路は無効にして測った。sparseは密な入力には走らせていない。

参照元は固定revisionであり、Library Checkerの順位や最新・最速の実装を確認したという意味ではない。

- [Nyaanの多変数FPS](https://github.com/NyaanNyaan/library/blob/b3981adc80a800b2584980b01821324ea6c77183/fps/multivariate-fps.hpp): `b3981adc80a800b2584980b01821324ea6c77183`
- [maspypyの2変数逆数](https://github.com/maspypy/library/blob/ede5df59c235e19937893bff5fc59c6f94aa06d4/poly/2d/fps_inv_2d.hpp)、[exp](https://github.com/maspypy/library/blob/ede5df59c235e19937893bff5fc59c6f94aa06d4/poly/2d/fps_exp_2d.hpp): `ede5df59c235e19937893bff5fc59c6f94aa06d4`

### 条件

- WSL2、Ryzen 7 3700X、PyPy 3.10.14 / 7.3.16、g++ 13.3.0。法998244353。
- 各方式へ同じ係数列を渡す。新しいprocessで逐次実行し、順番を回ごとにずらす。各3回の中央値。特記しない表はウォームアップなし。
- 計算部分を測定。import・入力処理・出力は含まない。全体の経過時間もJSONに別途保存する。PyPy版では返却オブジェクトの生成を含む。
- 出力全係数のhashを照合する。時間切れは一致扱いにしない。小入力では独立した単純解とも照合する。
- 最大メモリは計算後の`/proc/self/status`の`VmHWM`。3試行中の最大値で、ランタイムや入力保持も含む。`ru_maxrss`は起動前の親の最大値が混ざる場合があったため比較には使わず、診断用に併記した。
- C++は`-std=c++20 -O3 -DNDEBUG`でビルド。maspypyのheader内の`Ofast,unroll-loops`・`avx2,popcnt`指定も有効。言語差だけを切り分けた測定ではない。
- 密な入力のseedは92471。冪の指数は1234567。expの定数項は0、他の演算は1。

### 密な入力

単位は秒。W×Hは各変数の打切り次数で、係数数はW*H。

| W×H | 演算 | current | colored | row | maspy C++ | Nyaan C++ |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 256×256 | inv | 0.333 | 0.153 | 0.194 | 0.0380 | 0.0217 |
| 256×256 | exp | 0.874 | 0.596 | 0.641 | 0.159 | 0.0841 |
| 16×4096 | inv | 0.334 | 0.140 | 0.270 | 0.0395 | 0.0206 |
| 16×4096 | exp | 0.846 | 0.579 | 0.725 | 0.161 | 0.0862 |
| 4096×16 | inv | 0.335 | 0.161 | 0.195 | 0.0412 | 0.0236 |
| 4096×16 | exp | 0.739 | 0.587 | 0.601 | 0.158 | 0.0897 |
| 127×521 | inv | 1.760 | 0.256 | 0.310 | 0.0682 | 0.0419 |
| 127×521 | exp | 3.278 | 2.236 | 2.591 | 0.316 | 0.197 |
| 512×512 | inv | 1.358 | 0.514 | 0.640 | 0.163 | 0.0932 |
| 512×512 | exp | 3.549 | 2.285 | 2.376 | 0.658 | 0.396 |

この範囲ではcoloredがPyPyの密な入力で一貫して速かった。逆数は約2.1〜6.9倍、expは約1.26〜1.55倍の短縮。ただし、512×512でもNyaan C++に対して逆数で約5.5倍、expで約5.8倍の時間がかかる。参照実装との差はまだ残っている。

メモリにも例外がある。127×521の逆数はcurrentの209.0MiBに対してcoloredが103.3MiBだったが、同じ形のexpは209.1→216.6MiBで増加した。512×512のexpは204.9→187.3MiB。速度だけを見て、常に省メモリとも判断しない。

### 別入力とウォームアップ後の確認

seedを92472へ変更し、各processで同じ計算を1回行ってから2回目を測定した。これだけでPyPyのJITが完全に安定したとは扱わない。メモリの最大値には1回目も含む。

| W×H | 演算 | current | colored | row | Nyaan C++ |
| --- | --- | ---: | ---: | ---: | ---: |
| 256×256 | inv | 0.274 | 0.109 | 0.126 | 0.0191 |
| 256×256 | exp | 0.787 | 0.540 | 0.558 | 0.0828 |
| 512×512 | inv | 1.267 | 0.469 | 0.592 | 0.0872 |
| 512×512 | exp | 3.526 | 2.237 | 2.179 | 0.385 |

逆数ではcoloredの優位が維持された。512×512のexpはrowが約2.6%速い中央値になったが、各3回の範囲はcoloredが2.179〜2.293秒、rowが2.140〜2.236秒と重なる。この差だけでexp全般の採用方式は決めない。seedとウォームアップの両方を変えたため、前の表との差をウォームアップだけの効果とも扱わない。

### NTTと端数処理の内訳

別の実行でNTTの呼出し回数と長さを数えた。これらの計測を挟んだ実行時間は速度表に使用していない。

| W×H | 演算 | 方式 | NTT回数 | 最大変換長 | 変換長×log2(変換長)の合計 |
| --- | --- | --- | ---: | ---: | ---: |
| 256×256 | inv | current | 60 | 262144 | 53310720 |
| 256×256 | inv | colored | 160 | 65536 | 19660820 |
| 256×256 | inv | row | 22053 | 512 | 16262154 |
| 127×521 | inv | current | 66 | 262144 | 81752064 |
| 127×521 | inv | colored | 170 | 131072 | 41943060 |
| 127×521 | exp | current | 459 | 262144 | 249613824 |
| 127×521 | exp | colored | 1596 | 262144 | 160395684 |

coloredは逆数の変換長と変換仕事量の目安を減らした。rowはこの合計がさらに小さい一方、短い変換の呼出しが非常に多く、今回のPyPy試作では逆数の時間はcoloredより長かった。この合計は点ごとの積・配列操作・端数処理を数えておらず、実時間そのものではない。

特に127×521には別の問題がある。`NTT998.multiply`は積の長さが2の冪を少し超えたとき、超過部分だけ直接計算してNTTを短くする。詰めた配列の長さ131687と130552の積で超過が94になるため、1回の補正で94×130552=12271888回の係数積が発生した。現行の逆数全体では24543904回、expでは36821040回。coloredの逆数では0回だが、外側の積が残るexpでは24543840回だった。非2冪サイズでの大きな時間差を、NTTの長さだけに帰属させてはいけない。

この補正だけを無効にする追加比較も行った。同じseed・新規process・各3回。次表は別の測定群なので、前の表と混ぜて倍率を計算しない。

| W×H | 演算 | current | current・補正なし | colored | colored・補正なし |
| --- | --- | ---: | ---: | ---: | ---: |
| 256×256 | inv | 0.316 | 0.324 | 0.149 | 0.143 |
| 256×256 | exp | 0.861 | 0.787 | 0.589 | 0.580 |
| 127×521 | inv | 1.701 | 0.628 | 0.258 | 0.255 |
| 127×521 | exp | 3.003 | 1.602 | 2.053 | 1.124 |

127×521のexpはcoloredと補正無効化を合わせると約2.67倍速かった。最大メモリもcurrentの209.0MiBから126.9MiBへ減った。coloredだけの場合の216.2MiBという増加も回避した。coloredの逆数には元々この補正がないので、その列の小差は別方式の効果ではない。

ただし、256×256の現行逆数では補正を無効にして速くなったとはいえない。既存の1変数FPSなどへの影響も未検証。補正を一律に削除するのではなく、超過項数だけでなく係数積の回数とNTTを延長するコストを比較する条件が次の候補になる。

### 疎な入力

256×256。Kは定数項以外の非零項数。「低次数」はxとyの次数の和が小さい順にK個を配置。「ランダム」は全域からK位置を選ぶ。前者では計算結果が密になりやすく、後者では高い次数のため寄与が途中で打ち切られやすい。

| 配置 | K | 演算 | current | colored | sparse |
| --- | ---: | --- | ---: | ---: | ---: |
| 低次数 | 16 | inv | 0.0288 | 0.141 | 0.0286 |
| 低次数 | 17 | inv | 0.317 | 0.145 | 0.0285 |
| 低次数 | 64 | inv | 0.315 | 0.146 | 0.0821 |
| 低次数 | 128 | inv | 0.320 | 0.143 | 0.188 |
| ランダム | 128 | inv | 0.315 | 0.133 | 0.0443 |
| 低次数 | 17 | log | 0.398 | 0.222 | 0.0252 |
| 低次数 | 17 | exp | 0.850 | 0.591 | 0.0236 |
| 低次数 | 128 | exp | 0.922 | 0.613 | 0.163 |
| 低次数 | 17 | pow | 1.268 | 0.794 | 0.0280 |

現行の16項という切替条件は、この測定では小さすぎた。17項のexpはsparseで約36倍、powは約45倍速い。一方、低次数128項の逆数ではcoloredのほうが速い。同じ128項でも配置によって勝つ方式が変わるため、全演算へ同じ閾値を設定するのではなく、演算・サイズ・次数配置を含めて決める余地がある。上の倍率には疎な経路の維持と固定係数の前計算の両方が含まれる。

### 再現用ファイル

- `benchmarks/bivariate_candidates.py`: 本体とは分離した試作。
- `benchmarks/compare_bivariate_methods.py`: 同じ入力の生成、逐次実行、結果照合、原子的なJSON保存。
- `benchmarks/bivariate_reference.cpp`: C++参照実装を呼ぶadapter。参照library自体はrepository外へ固定revisionで用意する。
- `benchmarks/profile_bivariate.py`: NTTの長さ・回数を数える。計測を挟んだ実行時間は速度比較に使わない。
- `benchmarks/compare_bivariate_boundary.py`: 端数補正の有無だけを変えた比較。
- `benchmarks/results/library_checker/bivariate-methods-*.json`: 入出力hash、source・実行ファイルhash、各回の時間とメモリ。
- `verify/test_bivariate_comparison.py`: 単純解との照合、部分的な精度、1変数へ退化した形、疎な入力の境界、測定後の関数復元。

repository rootからWSL/Linux上で実行する。参照headerの配置とrevisionを合わせてからC++をビルドする。

```sh
g++ -std=c++20 -O3 -DNDEBUG -DMASPY -I ../lc-comparison/maspy-bivariate-reference library_codex/benchmarks/bivariate_reference.cpp -o ../lc-comparison/bivariate-maspy
g++ -std=c++20 -O3 -DNDEBUG -I ../references/nyaan-library library_codex/benchmarks/bivariate_reference.cpp -o ../lc-comparison/bivariate-nyaan
pypy3 library_codex/benchmarks/compare_bivariate_methods.py --shapes 256x256 16x4096 4096x16 127x521 512x512 --operations inverse exponential --modes current colored row maspy nyaan --repeat 3 --maspy ../lc-comparison/bivariate-maspy --nyaan ../lc-comparison/bivariate-nyaan --output library_codex/benchmarks/results/library_checker/bivariate-methods-dense.json
pypy3 library_codex/benchmarks/compare_bivariate_methods.py --shapes 256x256 --operations inverse logarithm exponential power --families sparse-low sparse-random --terms 8 16 17 32 64 128 --modes current colored sparse --repeat 3 --output library_codex/benchmarks/results/library_checker/bivariate-methods-sparse.json
pypy3 library_codex/benchmarks/compare_bivariate_methods.py --shapes 256x256 512x512 --operations inverse exponential --modes current colored row nyaan --repeat 3 --warmups 1 --seed 92472 --nyaan ../lc-comparison/bivariate-nyaan --output library_codex/benchmarks/results/library_checker/bivariate-methods-warm.json
pypy3 library_codex/benchmarks/profile_bivariate.py --output library_codex/benchmarks/results/library_checker/bivariate-methods-transforms.json
pypy3 library_codex/benchmarks/compare_bivariate_boundary.py --output library_codex/benchmarks/results/library_checker/bivariate-methods-boundary.json
```

この比較から、coloredの逆数、疎密の切替条件、NTTの端数補正条件を採用候補とした。expは逆数を差し替えるだけではC++との差が残る。今回の比較だけで全サイズ・全演算の最良手法とは断定しない。

比較は78条件・738回が完走し、各条件内で全出力のhashが一致した。密な10条件、疎な48条件、退化形を含む小入力12条件、ウォームアップあり4条件、端数補正の切り分け4条件。小入力は各1回で正しさの確認用、他は各3回。NTTの計数12条件はこの実行回数に含めない。

関連14テストとcatalog同期検査が成功。本体はこの比較では変更しておらず、全体テスト・Library Checkerへの提出・push・サイト公開は行っていない。

## 2変数FPSの本体への採用

2026-09-30。比較後に依頼を受け、次の3点を本体へ採用した。公開APIと呼出し方は変えず、互換aliasや新たな設定項目は追加していない。

- `MultivariateFPS._inverse_prefix`: 998244353、2変数、両軸の長さが2以上、求める係数数が256以上のとき、変換済みの逆数を再利用する2色NTTを使う。小入力・退化形・他の法では従来の計算を維持する。NTTの変換長上限を超える入力では従来経路へ戻す。
- `MultivariateFPS._sparse_2d`: 逆数および指数−1の冪は最大64項、log・exp・他の冪は最大128項まで疎な漸化式を使う。実際の上限は、それぞれの最大値と`max(16, N//8)`の小さいほう。小さい係数列を高密度の漸化式へ切り替えすぎない。次数配置による細かな切替は採用していない。
- `NTT998.multiply`: 超過項数128以下という条件に加え、直接計算する係数積の上限を、下側の2冪長の2倍以内とした。それより多い場合は通常のNTTを使う。ただし下側の長さが998の変換長上限2^23のときは、従来の対応範囲を狭めないため端数補正を維持する。

行ごとの変換を保存するrow方式は本体には入れていない。C++との差を埋めるための追加の複雑化は、この時点では行わない。

### 採用後の再測定

採用直前の3ファイルをrepository外の`../lc-comparison/bivariate-adoption-baseline/`へ保存し、前の比較のsource hashと一致することを確認した。旧FPS・旧多変数乗算・旧NTTを組み合わせて、採用後と同じ入力で測定した。PyPy 3.10.14 / 7.3.16、新規process、ウォームアップなし、交互に各3回の中央値。最大メモリは`VmHWM`の3試行中の最大。

| 条件 | 採用前 | 採用後 | 最大メモリ 採用前→後 |
| --- | ---: | ---: | ---: |
| 512×512、密な逆数 | 1.336秒 | 0.525秒 | 142.6→124.5MiB |
| 127×521、密なexp | 3.184秒 | 1.166秒 | 204.3→125.6MiB |
| 256×256、低次数17項のexp | 0.924秒 | 0.0268秒 | 109.8→85.8MiB |

3条件18回すべて完走し、各条件内の入出力hashが一致した。生データは`benchmarks/results/library_checker/bivariate-adopted-*.json`。比較用のimportなどが前段の手法比較とは異なるため、メモリ値を測定群をまたいで直接比較しない。

```sh
pypy3 library_codex/benchmarks/compare_multivariate_fps.py --baseline ../lc-comparison/bivariate-adoption-baseline/MultivariateFPS.py --baseline-multiply ../lc-comparison/bivariate-adoption-baseline/MultivariateMultiplication.py --baseline-ntt ../lc-comparison/bivariate-adoption-baseline/NTT998.py --width 127 --height 521 --operation exponential --output library_codex/benchmarks/results/library_checker/bivariate-adopted-exp.json
```

比較用snapshotはGit管理外。再現するときはJSONのsource hashと一致する3ファイルを指定する。

### 採用後の検査

- 関連23テストが成功。独立した単純解、255・256・257係数での経路切替、短い入力からの精度延長、疎な項数上限の前後、端数補正の適用・回避を含む。
- `pypy3 library_codex/tools/check_library.py --profile full`が成功。全体743テスト、全体性能検査、API・catalog同期、説明監査、再帰監査を通した。単独実行の検査には新しい2色NTT経路も含む。
- 生成catalogは363 modulesのうち依存先を含む11 modulesを更新。公開APIの数や呼出し方は変えていない。
- この採用作業ではcommit・push・サイト公開は行っていない。

## 未採用の候補と参照先

maspypyのソースは比較用mirrorのrevision `ede5df59c235e19937893bff5fc59c6f94aa06d4`（2026-08-10）で確認した。最新版の全実装を比較し終えたという記録ではない。

- [maspypyの対数微分からの復元](https://github.com/maspypy/library/blob/main/poly/from_log_differentiation.hpp): F'/F=a/bでa,bが疎な場合、O(N(K_a+K_b))でFを復元する。exp(f/g)など、単にfを疎として扱うより広い用途を持つ。専用APIの追加は未実施。
- [maspypyのSPS合成](https://github.com/maspypy/library/blob/main/setfunc/sps_composition.hpp): 入力の次数付きzeta変換を段ごとに保存し再利用する。現行合成も O(n²2^n) なので、これは定数倍と追加メモリの比較になる。
- [NachiaのSPS power projection](https://github.com/NachiaVivias/cp-library/blob/main/Cpp/Include/nachia/bit-convolution/set-power-series-power-projection.hpp): 入力側の変換を保存し、転置側の反復で使い回す。既存のpower projectionに対する候補。今回そのcacheは追加していない。
- [NyaanのSPS合成](https://nyaannyaan.github.io/library/set-function/polynomial-composite-set-power-series.hpp): 入力の変換結果を保存する構成を確認した。

これらはソース調査であり、各作者のC++実装との実行時間比較済み、あるいは全演算が最速であるとは扱わない。

## 検証

- 合成・NTTの変更時点: 全体721テスト、API・catalog同期、説明・再帰監査が成功。
- 続く疎FPS・SPS: 専用18テストが成功。単純解との乱択比較、負の指数、次数0・不正値、合成数の法、131072係数の既知解、packageなしのstandalone実行を含む。
- 998専用の疎な処理: 既存FPS・合成の28テストが成功。逆数・exp・log・冪・平方根などの単純解比較を含む。
- 変更moduleと依存先を選択した`check_changed.py`: 98テスト成功。API・catalog同期、説明監査、変更箇所の再帰監査も成功。
- 続く2変数FPS: 関連54テスト成功。独立した係数対の積・逆数・有限級数のexpとの比較、負の冪、定数項が1以外の冪、退化した軸、3変数、疎密切替の境界、127×133の既知のexp・log、256×256の既知の逆数、記事例、standalone実行を含む。API・catalog同期、説明監査、再帰監査も成功。全体検査は再実行していない。
- 演算子の説明を登録できなかったAPI検査の不整合も修正。公開するPython protocol methodの一覧をmetadataに統一し、存在する演算子は受け付け、存在しない名前は引き続き拒否するテストを追加した。

全体検査を変更のたびに繰り返さず、後続変更には対応テストと差分検査を使う。
