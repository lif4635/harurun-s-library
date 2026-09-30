# Library Checkerの問題別検査

2026-09-30 JST。対象のlibrary revisionは `ace5a01f428420a1454ff2008c6bbd919f7ebf80`。
ライブラリ本体・API・サイトは変更せず、問題別の提出コード、入力生成、単純解、比較記録を追加した。

## 検査範囲

10問題について、取得時点で最新の公式テストにACしているPyPy提出の実行時間順1位を取得し、同じローカルPyPyで比較した。同着の順序と後日のランキングは固定しない。

- 42個の記録ファイル、106ケースで出力の全tokenが一致。
- うち31ケースは小入力で、独立した単純解とも照合。
- 残り75ケースは各実装を3回ずつ起動して測定。うち5ケースの恒等写像による合成は、参照提出とは独立に全係数を確認。
- 複数サイズの単純解照合、standalone実行、既存の関連テストを含む63 testsが通過。
- `check_library.py --skip-benchmarks`も成功。共通のquick testsは83件通過。API参照・カタログ同期、説明監査、再帰監査を含む。全件のfull検査と共通性能回帰は今回は実行していない。
- カタログ同期検査は成功。本体を変えていないため、サイトの再生成・公開はしていない。

これは独自生成ケースでの検査であり、公式テスト全件の実行やLibrary CheckerへのAC提出ではない。C++最速との実測比較も含まない。

## 条件

AMD Ryzen 7 3700X、WSL2、PyPy 3.10.14 / 7.3.16。
同じ一時directory、通常ファイルのstdin、起動・JIT・入出力を含む壁時計時間。
各回の実装順はseed固定で入れ替え、並列には実行しない。中央値を掲載する。
CPU固定・他アプリの停止はしていないので、小さい差を確定的な優劣とは扱わない。

判定基準は「その問題を解く提出全体」。ライブラリ側は現在のsourceから公式のbundle生成器で展開し、解答コードを付ける。外部提出は内容を確認した後、hashの一致を確認して実行する。入力・出力・sourceのSHA-256、取得日時、問題version、runtime、生の時間、最大RSSをJSONへ保存した。

RSSはPyPy・JIT・入出力を含むプロセス全体で、構造だけのメモリではない。
judge側の時間は異なる環境のため、下のローカル時間と直接比べない。

## 代表結果

すべて同じ行の入力を両実装へ与えた値。単位は秒。
「現在の解答」は後述の標準解答を指し、遅い場合でもAPIを変えて数値を合わせてはいない。

| 問題 | 入力 | 参照提出 | 現在の解答 | 時間比 |
| --- | --- | ---: | ---: | ---: |
| [Point Add Range Sum](https://judge.yosupo.jp/problem/point_add_range_sum) | N=Q=500,000、ランダム | 0.363 | 0.404 | 1.12 |
| [Range Affine Range Sum](https://judge.yosupo.jp/problem/range_affine_range_sum) | N=Q=500,000、ランダム区間 | 1.465 | 4.066 | 2.78 |
| [Predecessor Problem](https://judge.yosupo.jp/problem/predecessor_problem) | N=Q=1,000,000、ランダム | 0.289 | 0.517 | 1.79 |
| [Unionfind](https://judge.yosupo.jp/problem/unionfind) | N=Q=200,000、ランダム | 0.141 | 0.148 | 1.05 |
| [Lowest Common Ancestor](https://judge.yosupo.jp/problem/lca) | N=Q=500,000、ランダム木 | 0.528 | 1.628 | 3.09 |
| [Convolution](https://judge.yosupo.jp/problem/convolution_mod) | N=M=524,288、密な係数 | 0.522 | 0.735 | 1.41 |
| [Inv of Formal Power Series](https://judge.yosupo.jp/problem/inv_of_formal_power_series) | N=500,000、密な係数 | 0.410 | 0.779 | 1.90 |
| [Exp of Formal Power Series](https://judge.yosupo.jp/problem/exp_of_formal_power_series) | N=500,000、密な係数 | 0.622 | 1.215 | 1.95 |
| [Composition of Formal Power Series](https://judge.yosupo.jp/problem/composition_of_formal_power_series) | N=8,000、密な係数 | 0.196 | 0.239 | 1.22 |
| [Composition of Formal Power Series (Large)](https://judge.yosupo.jp/problem/composition_of_formal_power_series_large) | N=131,072、密な係数 | 2.702 | 3.025 | 1.12 |

LCAと区間アフィンの行は、標準解答・別解・参照を同時に再比較した記録から取った。ほかの行は各問題の最大測定profileから取った。異なる回の小さな時間変動を高速化の効果としない。

## Point Add Range Sum

- 参照: [339750](https://judge.yosupo.jp/submission/339750)。
- 現在の解答: BITを初期配列から構築し、点加算・区間和を直接呼ぶ。
- ランダムと、端点の更新・全体/一点の和を混ぜたケースを検査。
- 50万でランダムは0.404秒、境界中心は0.306秒。参照は0.363秒、0.289秒。
- ランダムの最大RSSは現在129.7MiB、参照134.6MiB。

今回の比較では差が小さく、優先して本体を変える根拠は弱い。参照は一括読み込みも使っており、差のすべてがBIT内部によるとは限らない。

[記録](../benchmarks/results/library_checker/problems/point_add_range_sum/point_add_range_sum-stress.json)

## Range Affine Range Sum

- 参照: [335682](https://judge.yosupo.jp/submission/335682)。
- 標準解答: LazySegTree、集計は整数、作用は係数2個のtuple。
- 別解: 同じLazySegTreeで、作用だけを1個の整数へ詰める。
- 係数0・1・mod−1、全区間、一点を含むケースも検査。作用の合成順は単純解と照合。

| 50万操作 | 参照 | tuple作用 | 整数作用 |
| --- | ---: | ---: | ---: |
| ランダム区間 | 1.465 | 4.066 | 2.360 |
| 全体/一点中心 | 0.517 | 0.606 | 0.619 |

ランダム入力の最大RSSはtuple版153.6MiB、整数版132.3MiB、参照144.2MiB。
整数版はこの問題の別解として保存したが、全入力で速いわけではない。
本体の汎用APIを整数作用専用へ変更していない。

参照は作用・集計値の表現、遅延伝播の処理、入力方法も異なる。tupleをなくすだけでは差は埋まらず、残りの内訳は追加の計測が必要。

[比較記録](../benchmarks/results/library_checker/problems/range_affine_range_sum/variants-range_affine_range_sum-stress.json)

## Predecessor Problem

- 参照: [283475](https://judge.yosupo.jp/submission/283475)。
- 現在の解答: FastSet。追加・削除・存在判定・以上の最小値・以下の最大値を使う。
- 初期集合が約半分埋まる入力と、約1/128だけ埋まる入力を検査。
- N=Q=100万で現在0.517/0.513秒、参照0.289/0.344秒。
- ランダムの最大RSSは現在97.7MiB、参照69.7MiB。

公式上限はN=1000万、Q=100万。今回N=1000万は未測定。
参照は32bitのarrayを階層化し、現在は64bit単位の整数listを使う。
初期構築、整数の桁数、保持形式を分けて調べる候補になるが、原因の割合までは未測定。

[記録](../benchmarks/results/library_checker/problems/predecessor_problem/predecessor_problem-stress-1000000.json)

## Unionfind

- 参照: [242332](https://judge.yosupo.jp/submission/242332)。
- 現在の解答: UnionFindのmergeとsame。
- 公式上限のN=Q=20万で、ランダムと順に辺を追加するケースを検査。
- 現在0.148/0.121秒、参照0.141/0.106秒。
- ランダムの最大RSSは現在68.6MiB、参照69.7MiB。

初回は誤って50万でも測定したが公式上限外だったため、正式な比較表と保存した問題別結果から除外した。生成器に上限チェックを追加し、20万で測り直した。

参照は親配列の経路短縮を解答ループ内へ直接書き、成分サイズやunion-by-sizeは保持しない。汎用UnionFindの機能を減らす置き換えは行わない。

[記録](../benchmarks/results/library_checker/problems/unionfind/unionfind-stress-200000.json)

## Lowest Common Ancestor

- 参照: [400748](https://judge.yosupo.jp/submission/400748)。
- 標準解答: LCA。Euler tourとRMQによる問い合わせ。
- 別解: 既存HeavyLightDecompositionのlcaを使う。
- ランダム・パス・星・平衡二分木を検査。

| N=Q=50万 | 参照 | LCA | HLD別解 |
| --- | ---: | ---: | ---: |
| ランダム | 0.528 | 1.628 | 1.419 |
| パス | 0.355 | 1.235 | 0.530 |
| 星 | 0.360 | 1.179 | 0.731 |
| 平衡二分木 | 0.468 | 1.145 | 0.822 |

ランダムの最大RSSは参照146.5MiB、LCA266.7MiB、HLD194.2MiB。
パスでのLCAは335.5MiBだった。

この問題では、参照がparent[v] < vの親配列を直接使い、隣接リストを組み立てない。一方、現在のLCAは森・複数成分の検査、Euler tour、RMQ用の組の保持まで行う。
今回の提出全体ではHLD別解が速いが、問い合わせだけの性能差やNに比べてQが極端に大きい場合は測っていない。
親配列からの構築と、汎用Euler/RMQのメモリを分けて調べる優先度が高い。

[比較記録](../benchmarks/results/library_checker/problems/lca/variants-lca-stress.json)

## Convolution

- 参照: [264889](https://judge.yosupo.jp/submission/264889)。
- 現在の解答: 998244353固定のmultiply。
- 密・疎・片方だけ長さ7の入力を検査。
- N=M=524288の密入力は現在0.735秒、参照0.522秒。
- 同入力の最大RSSは現在158.5MiB、参照178.1MiB。
- N=M=262145では現在0.382秒、参照0.370秒。2の冪境界直後の短い末尾を直接処理する現在の経路があるため、サイズによって差が変わる。

[公式上限の記録](../benchmarks/results/library_checker/problems/convolution_mod/convolution_mod-stress-524288.json)

## Inv of Formal Power Series

- 参照: [140558](https://judge.yosupo.jp/submission/140558)。
- 現在の解答: fps_inv。
- N=65536、262144、262145、500000で密・疎入力を検査。
- 50万の密入力は現在0.779秒、参照0.410秒。疎入力は現在0.210秒、参照0.390秒。
- 密入力の最大RSSは現在127.2MiB、参照91.9MiB。

疎入力の改善を維持しつつ、密入力の変換・一時配列・入出力を分けて調べる。現在の結果だけでは差の原因を断定しない。

[公式上限の記録](../benchmarks/results/library_checker/problems/inv_of_formal_power_series/inv_of_formal_power_series-stress-500000.json)

## Exp of Formal Power Series

- 参照: [319294](https://judge.yosupo.jp/submission/319294)。
- 現在の解答: fps_exp。
- N=65536、262144、262145、500000で密・疎入力を検査。
- 50万の密入力は現在1.215秒、参照0.622秒。疎入力は現在0.231秒、参照0.595秒。
- 密入力の最大RSSは現在155.5MiB、参照143.8MiB。

逆数と同様に密入力を優先して調べる。疎入力も含めて一律に差し替える根拠にはしない。

[公式上限の記録](../benchmarks/results/library_checker/problems/exp_of_formal_power_series/exp_of_formal_power_series-stress-500000.json)

## Composition of Formal Power Series

追加の[処理別計測とC++実装の調査](COMPOSITION_PROFILE.md)では、現在の時間の約88%が各段のNTT・逆NTTにあることと、C++上位の戻り側の変換長削減を確認した。

- 通常版の参照: [398299](https://judge.yosupo.jp/submission/398299)。公式上限N=8000。
- Large版の参照: [367593](https://judge.yosupo.jp/submission/367593)。公式上限N=131072。取得時点の最速PyPy提出はharurun4635名義。
- 現在の解答: `fps_compose(outer, inner, n)`。外側・内側を取り違えないよう、問題の2行目をouter、3行目をinnerへ渡す。
- 密入力、内側だけ疎な入力、内側が恒等写像の入力を検査。外側はどれも密な係数。
- 別解`trimmed`: 内側の末尾のゼロを除いてから、同じ関数へ渡す。ライブラリ本体は変更していない。

| 入力 | 参照提出 | 現在の解答 | 末尾ゼロを除く別解 |
| --- | ---: | ---: | ---: |
| 通常版、N=8000、密 | 0.196 | 0.239 | 0.220 |
| Large、N=65535、密 | 1.324 | 1.385 | 1.394 |
| Large、N=65536、密 | 1.406 | 1.421 | 1.452 |
| Large、N=65537、密 | 2.723 | 2.774 | 2.756 |
| Large、N=131072、密 | 2.702 | 3.025 | 3.034 |
| Large、N=131072、内側だけ疎 | 2.828 | 2.784 | 2.656 |
| Large、N=131072、恒等写像 | 2.794 | 2.558 | 0.111 |

密な最大入力では約12%遅い一方、最大RSSは現在138.4MiB、参照423.5MiB。参照へ単純に置き換えると、この測定ではメモリ面の利点を失う。
密入力では末尾ゼロを除く処理は実質何も変えない。そこで生じる数%の差を最適化の効果とは扱わない。

### 恒等写像を長い配列で渡す場合

`inner=[0, 1]`は専用の高速経路へ入るが、`[0, 1, 0, ..., 0]`を渡すと一般合成へ入る。
同じ意味の入力なのに、N=131072では末尾ゼロの除去だけで約2.558秒から約0.111秒になった。
出力は元のouterと全係数一致することも確認した。一般合成の改良と切り離して直せる明確な候補。

### 2の冪の直後

N=65536から65537で、現在は約1.95倍、参照は約1.94倍に増えた。
両実装とも内部長を次の2の冪へ丸めるため、この境界で変換長が倍になる。現在の実装だけの異常ではないが、改善の余地はある。
末尾ゼロの除去では密入力のこの問題は解決しない。

### 密な合成の次の調査

現在も参照も計算量は`O(N log² N)`の系統。現在は下降時の変換結果を`array('I')`で保存し、上昇時に再利用する。
再帰の有無だけで速度差を説明する根拠はない。NTT本体、周波数配列の反転・コピー、一時配列の変換を個別に計測し、メモリの利点を維持して詰める。
今回、これら各処理への時間配分までは計測していない。

[通常版の記録](../benchmarks/results/library_checker/problems/composition_of_formal_power_series/composition_of_formal_power_series-large.json) · [Large上限の記録](../benchmarks/results/library_checker/problems/composition_of_formal_power_series_large/composition_of_formal_power_series_large-stress.json) · [境界直後の記録](../benchmarks/results/library_checker/problems/composition_of_formal_power_series_large/composition_of_formal_power_series_large-stress-65537.json)

## 次に調べる候補

1. 合成: 長いゼロ末尾で高速経路へ入らない問題。密入力はメモリを抑えたまま定数倍を調べる。
2. LCA問題: 親配列からの構築とEuler/RMQの保持形式。時間とメモリの両方。
3. Range Affine Range Sum: 整数作用の別解を基準に、残る遅延伝播・呼出しの負担。
4. Inv/Exp: 密入力の変換と一時配列。疎入力の性能は維持する。
5. Predecessor: 32bit/64bitの保持形式と初期構築。N=1000万は別途測る。
6. Convolution: 2の冪とその前後、密入力。単一サイズだけで採否を決めない。

本体の修正はこの検査では行っていない。

## 再実行と追加方法

解答・入力生成・単純解は `benchmarks/lc_problems/<problem>.py` にまとめた。
新しい問題はここへ追加し、ライブラリのclass名からではなくLibrary Checkerのproblem IDで選ぶ。
`MODULE`は標準解答に使うmodule、`VARIANTS`は同じ問題の別解。
`FAMILIES`は入力の種類、`MIN_SIZE/MAX_SIZE`はこの生成器が使うサイズの許容範囲。

提出取得と測定は分離している。取得だけで外部sourceを実行しない。
キャッシュはrepository外に置き、外部sourceは再配布しない。

```sh
pypy3 library_codex/benchmarks/library_checker_suite.py fetch --cache ../lc-comparison
pypy3 library_codex/benchmarks/library_checker_suite.py small --cache ../lc-comparison --reviewed 264889 319294 140558 400748 339750 283475 335682 242332 398299 367593 --output ../lc-comparison/problems
pypy3 library_codex/benchmarks/library_checker_suite.py large --cache ../lc-comparison --reviewed 264889 319294 140558 400748 339750 283475 335682 242332 398299 367593 --output ../lc-comparison/problems
pypy3 library_codex/benchmarks/library_checker_suite.py stress --cache ../lc-comparison --reviewed 264889 319294 140558 400748 339750 283475 335682 242332 398299 367593 --output ../lc-comparison/problems
```

IDは今回確認した提出。ランキングを再取得したら、新しいsourceを読んで確認してからIDを渡す。
過去の再現には保存したsnapshotと同じhashのキャッシュを使う。
`--problems lca range_affine_range_sum`のように問題単位で絞れ、`--size`でサイズを指定できる。
入力制約外のsizeは拒否する。Predecessor生成器はN=Qなので、許可するsizeはQ上限の100万まで。

```sh
pypy3 library_codex/benchmarks/library_checker_suite.py stress --size 500000 --problems inv_of_formal_power_series exp_of_formal_power_series --cache ../lc-comparison --reviewed 140558 319294 --output ../lc-comparison/problems
pypy3 library_codex/benchmarks/library_checker_suite.py stress --size 524288 --problems convolution_mod --cache ../lc-comparison --reviewed 264889 --output ../lc-comparison/problems
pypy3 -m pytest -q library_codex/verify/test_library_checker_benchmark.py
```

`large`は通常問題でN=Q=10万、FPS/畳み込みでN=65536。
`stress`は通常問題でN=Q=50万、Unionfindだけ20万、FPS/畳み込みは262145。
いずれも各生成器の上限で止めるため、合成は通常版8000、Large版131072になる。
公式上限の全ケースを意味する名前ではない。
