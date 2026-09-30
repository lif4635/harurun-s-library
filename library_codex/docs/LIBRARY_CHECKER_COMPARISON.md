# Library Checkerとの速度比較

追加の8問題と問題別の解答比較は[問題別検査](LIBRARY_CHECKER_PROBLEMS.md)にまとめています。

測定日: 2026-09-30 JST。変更前のlibrary revision: `2e29669e13ed3dc5485c866866a597b4594bce37`。

## 今回の範囲

- Set Xor-Min: 取得時点の最新テストでACのPyPy上位2提出とBinaryTrie。
- Vertex Add Subtree Sum: 同条件のPyPy上位2提出とHLD＋BIT、DSU on Tree＋時刻方向のBIT。
- DSU on Tree: 変更前後で同じ色の種類数を集計する単体比較。

全言語・全問題の最速実装と比較し終えたわけではない。C++のSet Xor-Min最上位提出も調べたが、ローカル実行・移植はしていない。今回の比較入力は公式形式の独自生成ケースで、公式テスト全件の再実行や新しいAC提出は行っていない。

## 比較対象と条件

公式APIから、ACかつ`is_latest`の提出を実行時間順に取得した。同着の順序と、その後のランキング更新は固定できない。取得日時、問題・テストのversion、提出URL、sourceのSHA-256、言語情報を各結果JSONの`snapshot`に保存している。

| 問題 | 提出 | 取得時のjudge時間 |
| --- | --- | ---: |
| Set Xor-Min | [387904](https://judge.yosupo.jp/submission/387904) | 0.570秒 |
| Set Xor-Min | [287605](https://judge.yosupo.jp/submission/287605) | 0.729秒 |
| Vertex Add Subtree Sum | [400751](https://judge.yosupo.jp/submission/400751) | 0.425秒 |
| Vertex Add Subtree Sum | [388446](https://judge.yosupo.jp/submission/388446) | 0.496秒 |

ローカル条件:

- Windows上のWSL2、AMD Ryzen 7 3700X。PyPy 3.10.14 / 7.3.16。
- judgeのPyPyは取得時の言語情報では3.9 / 7.3.9。judgeの秒数とローカルの秒数を直接比較しない。
- 比較実装はすべて同じ一時directoryへコピーし、同じPyPyで順次実行。1プロセスずつで、CPU固定や他アプリの停止はしていない。
- 提出全体の比較は毎回新しいプロセスを起動し、起動・JIT・入出力を含む壁時計時間を5回測定して中央値を使う。各回の実装順はseed固定で入れ替える。
- stdinは全実装で通常ファイル。最上位提出の`os.fstat(0).st_size`を使う入力にも合わせる。
- seedは92471。入力・出力・standalone sourceのSHA-256と生の時間、プロセス最大RSSを保存。
- 小入力は単純解と照合。大入力では出力の全tokenを相互照合し、不一致なら測定を中止する。
- メモリはPyPy本体・JIT・入出力も含むプロセス最大RSS。データ構造だけの使用量ではない。

## BinaryTrie

Q=500,000、単位は秒。

| 入力 | 387904 | 287605 | library | library / 387904 |
| --- | ---: | ---: | ---: | ---: |
| 30bitランダム | 0.667 | 0.959 | 0.974 | 1.46 |
| 比較的密な値域 | 0.683 | 0.746 | 0.851 | 1.25 |
| 128種類・重複多数 | 0.281 | 0.322 | 0.252 | 0.90 |
| 上位bit共通 | 0.468 | 0.463 | 0.493 | 1.05 |

最初の1/4は追加、残りは追加・削除・問い合わせを約4:2:4で混ぜる。問い合わせ時は非空。存在しない値の削除、登録済みの値の追加も含む。各入力の正確な生成手順は`benchmarks/library_checker_cases.py`を正本とする。

387904は集合専用の圧縮trie。大きな配列を先に確保し、葉に値を符号化する。libraryはmultiset・全体xor・順位検索を持ち、今回の集合用adapterは追加前に存在確認するため、探索の負担も異なる。

ランダム50万操作の最大RSSは387904が約103MiB、libraryが約115MiB。重複多数では約101MiBと約74MiB。10万操作だけでは見えにくかった速度差が50万操作では明確になった。今回はBinaryTrieの機能を削って置き換えてはいない。

今後の候補は、集合としての追加で二重探索を避ける方法、葉の値の表現、配列拡張の頻度。multiset・lazy xor・rankなどを維持した同条件比較が必要。

生データ: [10万操作](../benchmarks/results/library_checker/xor-100k.json)、[50万操作](../benchmarks/results/library_checker/xor-500k.json)。

## 部分木和

N=Q=100,000、単位は秒。library DSUは今回の変更後。

| 木 | 400751 | 388446 | library HLD＋BIT | library DSU |
| --- | ---: | ---: | ---: | ---: |
| ランダム | 0.149 | 0.155 | 0.241 | 0.730 |
| パス | 0.147 | 0.149 | 0.164 | 0.318 |
| 星 | 0.137 | 0.142 | 0.173 | 0.383 |
| 平衡二分木 | 0.147 | 0.166 | 0.198 | 0.686 |

上位2提出はDSU on Treeではなく、親配列を使ったEuler順/HLD＋BIT。問題の`parent[v] < v`という条件を直接利用し、無向隣接リストを組み立てない。汎用HLDと同じ入力API・機能ではない。

DSU版は更新履歴を頂点ごとに持ち、時刻方向のBITへ追加・削除するoffline解法。頂点の追加・削除自体が重く、この問題ではEuler順＋BITが適する。DSUという技法の性能を、この問題の最速順位だけで評価しない。

生データ: [変更前](../benchmarks/results/library_checker/subtree-100k.json)、[変更後](../benchmarks/results/library_checker/subtree-100k-after.json)。独立した測定なので、前後差には実行環境の揺れも含む。

## 採用したDSU on Treeの変更

`run`の状態スタックを廃止し、重い子を先に並べたEuler順を逆から読む。親に進むときは重い子の集計が残っており、残りの連続区間を追加すればよい。軽い子の根でのみその部分木を削除する。

- callback回数と答えは変更前後で一致。
- `run`自体の追加領域はO(1)。構築・保持する配列は従来どおりO(N)。
- callbackの順序は変わる。各`query(v)`の集計対象がvの部分木と一致する契約は維持する。
- constructorは変更していない。構築時間の変動を改善として数えない。

10万頂点、色は`v % 97`。小入力3回でウォームアップし、7回の`run`時間の中央値を取る。初回の順序は旧→新、確認測定は新→旧。各実装は別プロセス。

| 木 | 初回 旧→新 (ms) | 確認測定 旧→新 (ms) |
| --- | ---: | ---: |
| ランダム | 77.35 → 15.37 | 88.79 → 20.74 |
| パス | 27.04 → 0.93 | 52.21 → 0.72 |
| 星 | 44.76 → 1.59 | 35.06 → 1.80 |
| 平衡二分木 | 35.25 → 16.85 | 33.81 → 18.28 |

軽いcallbackではJITの最適化を受けやすく、特にパス・星では大きな差が出る。callbackがBIT操作などで重くなれば、処理全体の改善率は小さくなる。この倍率を一般の用途へそのまま当てはめない。

生データ: [初回](../benchmarks/results/library_checker/dsu-core.json)、[確認測定](../benchmarks/results/library_checker/dsu-core-confirm.json)。変更前の自作実装は`benchmarks/_dsu_on_tree_baseline.py`に固定している。

## 再実行

repository rootから実行する。WSL/LinuxのPyPyと`/usr/bin/time`が必要。外部提出のsourceはリポジトリ外へ保存し、ライセンス未確認のコードを配布ZIPへ混ぜない。

```sh
pypy3 library_codex/benchmarks/library_checker.py fetch --problem set_xor_min --top 2 --cache ../lc-comparison
pypy3 library_codex/benchmarks/library_checker.py fetch --problem vertex_add_subtree_sum --top 2 --cache ../lc-comparison
```

取得したsourceを読み、安全性・入出力・比較対象を確認してから、実際のIDを`--reviewed`へ渡す。取得しただけでは実行しない。sourceが取得時のhashと異なる場合も実行を拒否する。

以下のIDは今回のもの。後日のランキングから取得したIDへ無条件で置き換えず、改めて確認する。

```sh
pypy3 library_codex/benchmarks/library_checker.py compare --snapshot ../lc-comparison/set_xor_min-pypy3.json --reviewed 387904 287605 --size 500000 --families random dense duplicates prefix --repeat 5 --output ../lc-comparison/xor-500k.json
pypy3 library_codex/benchmarks/library_checker.py compare --snapshot ../lc-comparison/vertex_add_subtree_sum-pypy3.json --reviewed 400751 388446 --size 100000 --families random chain star balanced --repeat 5 --output ../lc-comparison/subtree-100k-after.json
pypy3 library_codex/benchmarks/dsu_on_tree.py --reverse-order --output ../lc-comparison/dsu-core-confirm.json
pypy3 -m pytest -q library_codex/verify/test_library_checker_benchmark.py library_codex/verify/tree/test_dsu_on_tree.py
```

別の問題を追加する場合は、`library_checker_cases.py`へ入力生成・単純解・standalone adapterを追加し、小入力照合をtestへ登録する。データ構造のcore時間と、起動・入力・問題専用処理を含む提出時間を分けて記録する。
