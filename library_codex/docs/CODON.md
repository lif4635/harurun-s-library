# Codon用の提出コード

元の`library_codex`を正本にしたまま、Codon向けのコードを生成します。関数名と呼び出し方は維持します。ライブラリを手作業で二重管理しません。

## 使い方

解法だけを`solution.py`へ置き、必要なmoduleを指定します。`solution.py`にはライブラリのimportを書かず、いつもの関数・class名を使います。

```sh
pypy3 library_codex/tools/build_codon.py fenwick_tree/BIT --solution solution.py --output Main.py
codon build --release -o a.out Main.py
./a.out < input.txt
```

`Main.py`をAtCoderの`Python (Codon 0.19.3)`へ提出します。`--solution`を省略するとライブラリ部分だけを出力します。`--list`で生成対象を確認できます。

生成したコードはCodon専用です。元のライブラリ、元の解法ファイルは書き換えません。出力先が`library_codex`内の場合は、実装の上書きを防ぐため`generated/`配下だけを許可します。

## 先頭への追加だけでは済まない箇所

Codon 0.19.3では、元のclassの`__slots__`と属性推論、class内のmethod alias、変数の型変更、`array`のimportなどがコンパイルを妨げます。また、PyPyの任意精度整数と違い、通常の整数は64bitです。NTTの積和をそのまま移すと、コンパイルできても答えが変わることがあります。

生成処理が必要な型情報を補い、対応する構文を変換します。998用のNTT・FPSは中間積も64bitで計算します。大きな入力係数は掛け算の前に正規化し、積和と3項以上の積ではあふれる前に剰余を取ります。NTTの蝶演算には不要な剰余を追加しません。符号付き剰余と負の指数のmodべき乗も補います。補助処理は`templates/codon_header.codon`が正本です。

汎用べき乗`_codon_pow`はmodが±998244353なら64bitの専用処理を使います。それ以外は、64bitに収まるmodでも係数の積が64bitを超え得るため、128bitを使います。998の演算を一律に128bit化する処理はありません。

正規化済み係数について、modを998244353とすると次が成り立ちます。

$$
(998244353-1)^2 = 996491786299899904 < 2^{63}-1.
$$

順変換の蝶演算で最大3個の積を足す箇所も64bitに収まります。一方、60個の積を貯める処理や、平方根の「差を作ってからもう一度掛ける」式にはこの保証がありません。生成コードでは積和を各回で剰余に戻し、平方根は差の剰余を取ってから次の係数を掛けます。

ヘッダーだけで任意のPythonコードが動くわけではありません。`--solution`の内容は変換せず、そのまま末尾へ置きます。

## 現在の範囲

| module | 対象 |
| --- | --- |
| `union_find/UnionFind` | 整数番号の頂点、併合、連結判定、成分列挙 |
| `fenwick_tree/BIT` | 整数の一点更新、区間和、境界探索 |
| `segment_tree/SegTree` | 一点更新、区間積、境界探索。整数・文字列・整数tupleのモノイド |
| `convolution/NTT998` | 整数係数listの畳み込み、二乗、順・逆変換 |
| `fps998/FPS` | 整数係数listの逆数・除算・log・exp・pow・sqrt・Taylor shiftなど |

これはライブラリ全体のCodon対応ではありません。合成、二変数FPS、集合冪級数、その他のmoduleは未対応です。未対応のmoduleは生成時にエラーにします。複数moduleを指定してまとめる機能もまだありません。FPSが必要とするNTTなどの内部依存は自動で含まれます。

制約:

- 解法側の型はCodonで推論できる必要があります。実行中にintからlistへ変わる変数などは使えません。
- BITは整数用です。floatのBITはこの生成処理の対象外です。
- SegTreeの演算・単位元・要素の型は一致させます。任意のPython objectや実行中の型変更は保証しません。
- NTT・FPSの係数は`list[int]`です。直接`ntt`・`intt`を呼ぶ際は係数をmodで正規化しておきます。
- 解法側の整数演算とデータ構造の和は、途中の計算も符号付き64bitに収めます。FPSの次数と指数の積など、係数のmod演算以外にもこの制約があります。
- NTTの`array("I")`はCodonの整数listへ変換します。係数表の要素あたりの領域は4byteから8byteになります。
- `sys.stdin.readline()`は補助処理で使えます。`sys.stdin.buffer`やPython標準ライブラリ全体の互換性は提供しません。
- 整数の`//`・`%`はヘッダーで負数もPythonと同じ向きに丸めます。解法側の`pow(a, b, m)`は書き換えません。負の指数や、途中の積が64bitを超えるmodでは補助関数`_codon_pow(a, b, m)`を使います。
- `(-2**63) // -1`は結果が64bitを超えるため`OverflowError`です。`(-2**63) % -1`は0を返します。
- CPythonへの処理委譲や`libpython`は使いません。

対象言語は[AtCoderの言語一覧](https://img.atcoder.jp/file/language-update/2025-10/language-list.html)に合わせています。Codonの制約は[公式ドキュメント](https://docs.exaloop.io/language/overview/)も参照してください。ローカル検証とAtCoderのACは別で、オンラインジャッジへの提出検証はまだ行っていません。

## 検証と追加

```sh
pypy3 -m pytest -q library_codex/verify/test_codon.py
pypy3 library_codex/benchmarks/compare_codon.py --size 32768 --repeat 3 --output codon-results.json
```

恒久テストは元の実装と生成コードに同じ解法・入力を与え、標準出力を比較します。畳み込みの単純解、FPSの逆数・log/exp・平方根の恒等式、空入力、負の係数、64bit境界、負の指数も検査します。生成失敗時に以前のファイルが残ることも確認します。

64bit境界の係数を含む疎・密の切替、NTTサイズ境界の補正、±64bit境界の指数も検査します。FPSのbundle内で名前が変わる依存関数にも同じ対策が適用されることを確認します。個別の式の変換規則は`build_codon.py`の`REDUCTIONS`に置き、対象の式が変わった場合は生成を止めて再確認します。

Codon 0.19.3がない環境ではネイティブ実行テストをskipし、そのことを表示します。skipはCodonでの検証成功ではありません。`check_changed.py`は対応module・変換処理・ヘッダーの変更時にこのテストを選び、通常検査にも含めます。

比較スクリプトは逐次実行し、各処理系の最初の1回を除いた中央値、全測定値、処理系の版、コードと出力のハッシュを記録します。起動・入出力を含み、コンパイル時間は別記します。AtCoderと異なるPyPyの版で測った結果を、AtCoderでの速度として扱わないでください。

対象を増やす場合は、変換処理の許可一覧、module別の比較ケース、必要な変換を追加し、Codon実機で確認します。コンパイル成功だけを理由に許可一覧へ加えません。既存APIやPyPyの高速な実装をCodonの都合で変更しないでください。

## 測定記録

### 64bit化後

2026-10-04、WSL、Codon 0.19.3、サイズ131072。初回を除く3回の中央値で、コンパイル時間を除き、起動・入出力を含みます。変更前はcommit `1277a19075afbbae17fea563bfa524736e1d1cb4`から生成した128bit版です。同じ比較コード・入力を逐次実行し、PyPyを含む3者で出力を照合します。FPSの値は複数演算と恒等式チェックの合計で、個々の演算の速度ではありません。

| 比較ケース | PyPy | Codon変更前 | Codon変更後 |
| --- | ---: | ---: | ---: |
| NTT998 | 0.3524秒 | 0.2989秒 | 0.1992秒 |
| FPS | 2.5642秒 | 2.4230秒 | 1.0189秒 |

今回の中央値では変更前に対して約1.50倍・2.38倍です。全759 tests、API・catalog同期、説明・再帰監査、full性能回帰を通過しました。オンライン提出は行っていません。

測定値は[変更前後の記録](../benchmarks/results/codon_arithmetic.json)に保存します。再測定する場合、変更前に生成した`NTT998.py`と`FPS.py`を同じdirectoryへ保存し、次を実行します。

```sh
pypy3 library_codex/benchmarks/compare_codon.py convolution/NTT998 fps998/FPS --size 131072 --repeat 3 --baseline-dir /path/to/baseline --baseline-label REVISION --output library_codex/benchmarks/results/codon_arithmetic.json
```

### 初期の128bit版

2026-10-03、WSLのCodon 0.19.3とPyPy 7.3.16で測定。サイズ32768、初回を除く3回の中央値です。FPSは複数演算と恒等式チェックを含む合計で、個々の演算の速度ではありません。

| 比較ケース | PyPy | Codon |
| --- | ---: | ---: |
| UnionFind | 0.0674秒 | 0.0441秒 |
| BIT | 0.0643秒 | 0.0319秒 |
| SegTree | 0.0741秒 | 0.0358秒 |
| NTT998 | 0.1199秒 | 0.0949秒 |
| FPS | 0.5655秒 | 0.5319秒 |

全ケースで出力が一致しました。ただし短いケースは起動時間の影響が大きく、FPSでは改善は小幅です。高速化済みのPyPy実装をCodonへ移すだけで大幅に速くなるとは限りません。[生の測定値](../benchmarks/results/codon.json)に条件とコードのハッシュを保存しています。
