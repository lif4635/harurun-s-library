# 子孫参照セグメント木のclass化

## 比較対象

- 旧版: `build`・`update`・`fold`を使うKeyboard。mainの`92129db27f2554b13747b6ea91a88d58ddb64db8`時点の単独提出コードを`benchmarks/experiments/keyboard_functions.py`へ保存した。
- class版: `SegTreeTraversal(merge, identity, values)`を内部に持つKeyboard。同じmergeを構築・更新・区間取得で使う。
- 両方ともノードごとのobjectを保持せず、32bit整数配列と10の冪の表を使う。class版のstorageは木全体に1個だけ作る。

## 測定条件

PyPy 7.3.16 / Python 3.10.14、WSL Linux、Ryzen 7 3700X。同じ環境で1 processずつ実行し、各回を新しいprocessにした。事前warmupなし。各組の実行順は交互に反転する。このPyPyは`os.sched_setaffinity`に対応しておらず、CPU固定は行えていない（記録のaffinityはnull）。OS全体の負荷も隔離していない。実行環境・ソースと入力のSHA-256・各回の値はJSONに保存している。

N=8,000,000、Q=200,000。更新と区間取得を半分ずつ含む固定seedの独自入力で、公式の全ケース検証やオンラインACではない。

- mixed: 数字とBを混ぜた初期列。
- digits: 初期列は数字のみ。操作列にはBへの更新もある。
- cancellation: 数字63個とB32個を繰り返す初期列。子孫へ降りる結合が多い。

全出力を期待値と比較し、新旧の出力SHA-256も一致した。独立した単純解との比較は小規模randomized testで行う。最大入力の期待値生成はclass版であり、それ自体を独立oracleとは扱わない。

## 提出コード全体

入力生成を除き、起動・JIT・標準入出力・終了を含む。各5回の中央値。RSSは子process自身の最大常駐メモリの中央値。

| 入力 | 旧版 | class版 | 時間の変化 | 旧版RSS | class版RSS |
| --- | ---: | ---: | ---: | ---: | ---: |
| mixed | 2.078秒 | 1.940秒 | -6.6% | 334.3 MiB | 335.5 MiB |
| digits | 1.212秒 | 1.203秒 | -0.8% | 333.4 MiB | 333.6 MiB |
| cancellation | 2.056秒 | 2.175秒 | +5.8% | 335.6 MiB | 337.1 MiB |

class版は全入力で速くなるわけではない。cancellationでは約0.12秒遅く、RSSは最大約1.5 MiB増えた。測定値には実行ごとの揺れがあり、差のすべてをclassの呼出し費用とは断定しない。利用側の構築・更新管理と重複した結合処理を減らす代わりの、小さいがゼロではない費用として記録する。

記録は`benchmarks/results/keyboard_class_standalone_mixed.json`、`keyboard_class_standalone_digits.json`、`keyboard_class_standalone_cancellation.json`。

## 構築と操作の内訳

`benchmarks/results/seg_tree_traversal_class_large.json`は、入力生成後の構築と操作を別々に計測する。起動・入出力は時間に含めず、RSSには入力生成も含むため、上のRSSと直接比較しない。

同じ最大規模で各5回。合計時間の中央値は、旧版からclass版へmixedが1.506→1.538秒、digitsが0.887→0.941秒、cancellationが2.145→2.245秒。こちらでも全面的な高速化とはいえない。子孫参照が不要な結合は、先頭部分を探すループへ入らず保存済みの値を使う。

## 再測定

リポジトリ直下で実行する。1 processずつ測る。

```sh
pypy3 verify/atcoder/build_keyboard.py
pypy3 -m pytest -q library_codex/verify/segment_tree/test_seg_tree_traversal.py
pypy3 -m library_codex.benchmarks.seg_tree_traversal --n 8000000 --q 200000 --repeat 5 --output library_codex/benchmarks/results/seg_tree_traversal_class_large.json
pypy3 -m verify.atcoder.benchmark_keyboard --case mixed --compare --repeat 5 --output library_codex/benchmarks/results/keyboard_class_standalone_mixed.json
pypy3 -m verify.atcoder.benchmark_keyboard --case digits --compare --repeat 5 --output library_codex/benchmarks/results/keyboard_class_standalone_digits.json
pypy3 -m verify.atcoder.benchmark_keyboard --case cancellation --compare --repeat 5 --output library_codex/benchmarks/results/keyboard_class_standalone_cancellation.json
```

## class化前の測定記録

以下は3関数版を採用した時点の記録。現在のAPIや現在の測定結果とは区別する。

2026-10-25測定。共通関数は`segment_tree/SegTreeTraversal.py`、利用例は`verify/atcoder/abc434_g.py`。通常の`SegTree`は変更していない。

### 比較条件

- PyPy 7.3.16 / Python 3.10.14、WSL2 Linux、CPU 2へ固定して逐次実行。
- 各回を新しいprocessで実行し、事前warmupなし。JIT時間を含む。
- 小規模比較は20万文字・3万操作、更新と取得を交互に実施。各候補3回の中央値。
- `mixed`は数字とBをほぼ同数、`digits`は数字のみで構築後にBを含む更新、`cancellation`は63桁と32個のBの繰り返しから開始する。
- 時間は構築と全操作の合計。入力生成・Pythonの起動・標準入出力は除く。RSSは入力生成を含むprocess全体の最大値。
- 同じseed・入力hash・結果checksumを照合。小さいケースの正しさは別途、単純な末尾削除と比較する。
- OS全体の負荷は隔離していない。細かい差はJITと実行時の揺れも含む。

### 区間走査と保存形式

| 方式 | mixed | digits | cancellation |
| --- | ---: | ---: | ---: |
| 共通関数・右端から直接切り出す方式 | 0.160秒 | 0.110秒 | 0.188秒 |
| 同じ走査をKeyboard.prodへ直接記述 | 0.176秒 | 0.104秒 | 0.214秒 |
| 左側ノードを一時listへ積む方式 | 0.209秒 | 0.154秒 | 0.264秒 |
| 直接切り出す方式・保存配列をlist化 | 0.191秒 | 0.126秒 | 0.258秒 |

右端から最大の整列済み区間を切り出す方式を採用した。`fold`自体はO(1)追加メモリで、callbackへ渡すのは実在するノードの整数添字だけ。直接記述との差はこの測定では小さく、共通化による一貫した大幅な悪化は見られなかった。あらゆるcallbackで同じ速度になる保証ではない。

Keyboardでは`array("I")`に個数・長さ・値を別々に保存する。ノードごとのclassやtupleを避け、内部ノードには左から残った数値をキャッシュする。逆数の表と再帰呼出しを使わず、必要な先頭桁だけを一方の子へ降りて求める。

[比較の生データ](../benchmarks/results/seg_tree_traversal_comparison.json)には全36試行、RSS、入力・source hash、環境情報を保存した。初期の探索記録は`seg_tree_traversal.json`、採用直後の確認は`seg_tree_traversal_selected.json`に残している。初期記録の`shared`は一時list方式であり、採用後の`shared`とは異なる。

### 上限サイズと提出コード

800万文字・20万操作で共通版と直接記述版を1回ずつ比較した。構築と操作の合計は、繰り返し相殺入力で2.084秒 / 1.986秒、数字中心入力で1.066秒 / 1.086秒。これは反復平均ではなく1回の測定。[生データ](../benchmarks/results/seg_tree_traversal_large.json)

さらに、依存を展開した`abc434_g_standalone.py`を隔離processで3回実行した。

- 入力は800万文字・20万操作の独自の繰り返し相殺ケース。
- 起動・JIT・標準入力の解析・標準出力をすべて含む。
- 2.451 / 2.339 / 2.465秒、中央値2.451秒。
- 最大RSSは343696 KiB、約335.6 MiB。
- 出力全文をimport版と照合した。大規模ケースの比較相手は同じアルゴリズムであり、独立した正当性検査は小さい入力の単純解比較が担当する。

[提出コードの測定記録](../benchmarks/results/keyboard_standalone.json)

公式ケース全件・オンライン提出は未実施。この測定だけからAtCoderでのACや3秒以内を保証しない。

### 再実行

リポジトリ直下で実行する。ベンチマークはLinux/WSL向け。WSL内の別のcheckoutを更新する必要はない。

```sh
pypy3 verify/atcoder/build_keyboard.py
pypy3 -m pytest -q library_codex/verify/segment_tree/test_seg_tree_traversal.py
taskset -c 2 pypy3 -m library_codex.benchmarks.seg_tree_traversal --variants shared inline stack lists --output library_codex/benchmarks/results/seg_tree_traversal_comparison.json
taskset -c 2 pypy3 -m verify.atcoder.benchmark_keyboard --output library_codex/benchmarks/results/keyboard_standalone.json
```

`build_keyboard.py --check`で保存済み提出コードとsourceの同期を検査できる。この検査は専用pytestにも含まれる。
