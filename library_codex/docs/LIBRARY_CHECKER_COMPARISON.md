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

## 二部マッチングの上位提出比較（2026-10-04）

最新問題版のACを時間順に取得し、PyPy3の先頭[399951](https://judge.yosupo.jp/submission/399951)（judge上0.476秒）と、C++23の先頭[396318](https://judge.yosupo.jp/submission/396318)（0.070秒）のアルゴリズムを確認した。C++17など別言語IDを含む全C++提出の順位は調べていない。

PyPy版は孤立頂点除去、CSR、多点始点探索、次数1・2の処理と縮約を併用する。C++23版は交互路の距離ラベルを使って未マッチの右頂点を再割当し、一定回数ごとに全体の距離を更新する。後者の方式を独立に実装し、辺走査と全体更新の回数に上限を設けて、残りを既存のHopcroft–Karpで解く形を採用した。外部提出のsourceは配布物へ追加していない。

PyPy最速提出だけを実行比較した。C++版はアルゴリズムの参照のみで、ローカル実行時間は未計測。比較はWSLの同じPyPy 3.10 / 7.3.16、新規process、実行順を入れ替えた5回の中央値。起動・JIT・入出力を含み、各出力は公式checkerで検証した。外部PyPy版は乱数を使うので、同じ正解でも出力ペアが変わる。

| 公式ケース | 変更前 a1076d2 | 採用版 | PyPy最速提出 |
|---|---:|---:|---:|
| augmented_cycle_02 | 2.976秒 | 0.558秒 | 0.396秒 |
| augmented_cycle_01 | 2.409秒 | 0.654秒 | 0.379秒 |
| many_paths_00 | 0.433秒 | 0.366秒 | 0.442秒 |
| cycle_00 | 0.331秒 | 0.337秒 | 0.188秒 |

この4ケース中の最大RSSは、変更前108612 KiB、採用版109084 KiB、外部PyPy版117796 KiB。難しかったaugmented cycleは約3.7〜5.3倍速くなったが、最速提出との差は残る。閉路は改善していない。4ケースの比較を全入力での優劣とはしない。

採用版は公式44ケースを5秒制限内で通過し、最も遅かったケースは0.678秒。これは別の全件実行での単発値であり、上表の中央値とは区別する。オンライン提出はしていない。

生データは[時間・RSS・各sourceと入出力のhash](../benchmarks/results/bipartitematching-comparison.json)、参照したC++23の順位とhashは[取得記録](../benchmarks/results/bipartitematching-cpp-reference.json)。変更前sourceはGitの`a1076d2:verify/library_checker/solutions/bipartitematching.py`から再現できる。

別解を許す問題向けに`official_comparison.py`を追加した。公式入力と期待出力のhashを照合し、文字列一致ではなく公式checkerで各回答を判定する。取得したsourceを確認してから実行する。

```sh
pypy3 library_codex/benchmarks/library_checker.py fetch --problem bipartitematching --language pypy3 --top 2 --cache ../lc-matching-reference
pypy3 library_codex/benchmarks/official_comparison.py --snapshot ../lc-matching-reference/bipartitematching-pypy3.json --reviewed 399951 --problem /home/harurun/.cache/harurun-library-checker/problems/graph/bipartitematching --cases augmented_cycle_02 augmented_cycle_01 many_paths_00 cycle_00 --variant baseline=../lc-matching-reference/baseline.py --variant candidate=verify/library_checker/solutions/bipartitematching.py --repeat 5 --output library_codex/benchmarks/results/bipartitematching-comparison.json
```

## 区間並列Union-Findの上位提出比較（2026-10-04）

最新問題版のPyPy3最速は[368362 / harurun4635](https://judge.yosupo.jp/submission/368362)、judge上1.805秒だった。全階層を固定幅配列へまとめ、代表探索と併合をhot loop内で処理する実装を確認した。

採用版では、親と成分サイズを負数方式の単一配列へまとめ、重複した代表探索を除いた。配列は通常32ビット、全階層の番号が収まらない場合は64ビットを使う。提出driverは入力全体の保持をやめ、クエリを1行ずつ読む。この比較はライブラリ本体だけでなく、その入出力改善も含む。通常listの平坦化だけの案は最大RSSが増えたため採用しなかった。

旧版は`a1076d2`のライブラリへ今回のdriver（入力一括読込版）を接続したもの。同じ公式入力、PyPy 3.10 / 7.3.16、新規process、順序を変えた5回の中央値で比較し、すべて公式checkerを通した。計測用timeoutは30秒なので、旧版の5秒超えも打ち切らず測っている。

| 公式ケース | 変更前 | 採用版 | PyPy最速提出 |
|---|---:|---:|---:|
| decr_period_03 | 5.458秒 | 2.816秒 | 2.593秒 |
| periodic_03 | 4.993秒 | 2.283秒 | 2.338秒 |
| random_01 | 4.547秒 | 2.215秒 | 3.031秒 |

この3ケース中の最大RSSは、変更前310236 KiB、採用版173036 KiB、最速提出236616 KiB。採用版はこの範囲では約1.9〜2.2倍速く、最大RSSを約44%削減した。最速提出より遅いケースも残るため、全入力で最速とは主張しない。

取得時の順位、sourceと入力のhash、各回の時間・RSSは[生データ](../benchmarks/results/range-parallel-unionfind-comparison.json)に保存した。外部提出sourceはリポジトリ外のcacheへ置く。

```sh
pypy3 library_codex/benchmarks/library_checker.py fetch --problem range_parallel_unionfind --language pypy3 --top 1 --cache ../lc-matching-reference
pypy3 library_codex/benchmarks/official_comparison.py --snapshot ../lc-matching-reference/range_parallel_unionfind-pypy3.json --reviewed 368362 --problem /home/harurun/.cache/harurun-library-checker/problems/data_structure/range_parallel_unionfind --cases decr_period_03 periodic_03 random_01 --variant baseline=../lc-matching-reference/range-parallel-baseline.py --variant candidate=verify/library_checker/solutions/range_parallel_unionfind.py --repeat 5 --output library_codex/benchmarks/results/range-parallel-unionfind-comparison.json
```

## mod 2行列の上位提出比較（2026-10-04）

取得時点の最新問題版・AC・PyPy3・時間昇順で、行列積の先頭[389256](https://judge.yosupo.jp/submission/389256)と逆行列の先頭[389266](https://judge.yosupo.jp/submission/389266)を確認した。judge上の時間はそれぞれ1.406秒・1.436秒。外部提出のsourceはリポジトリ外に置き、取得記録とSHA-256を比較JSONへ残している。

採用した変更は次のとおり。

- 行列積: 密な入力は8列ずつのXOR組合せ表を作り、1ビットずつの走査を減らす。疎な入力は従来の非零ビット列挙を使う。
- 階数・行列式: 全行を簡約形へ変形せず、最高位ビットごとの基底に追加する。非常に横長の行列では辞書を使い、列数分の配列を作らない。
- 逆行列: 128行以上では8列ずつピボットを選び、その組合せ表で他の行をまとめて消去する。ピボットが見つからなければ、その時点で非可逆と判定する。

同じ公式入力を同じPyPy 3.10 / 7.3.16で5回実行した中央値。各回は新しいprocessで起動・JIT・入出力を含み、実行順を入れ替え、すべて公式checkerを通している。オンライン提出は行っていない。

| 問題 / 公式ケース | 変更前 | 採用版 | 最速PyPy提出 |
| --- | ---: | ---: | ---: |
| 行列積 / max_random_00 | 3.374秒 | 1.711秒 | 1.899秒 |
| 行列積 / many_1_00 | 6.997秒 | 1.719秒 | 2.188秒 |
| 行列積 / middle_00 | 0.078秒 | 0.071秒 | 0.080秒 |
| 逆行列 / max_fullrank_00 | 7.930秒 | 2.410秒 | 2.433秒 |
| 逆行列 / lowrank_max_random_05 | 7.082秒 | 0.233秒 | 0.322秒 |
| 逆行列 / perm_max_random_00 | 1.625秒 | 0.175秒 | 0.283秒 |

行列積の変更前は`a748080`の実装、逆行列の変更前は本作業中にビット判定をANDへ変更した後・ブロック消去を導入する前の版。それぞれ[行列積baseline](../benchmarks/baselines/matrix_product_mod_2.py)、[逆行列baseline](../benchmarks/baselines/inverse_matrix_mod_2.py)へ単独実行コードを固定した。baselineは再利用するライブラリ本体ではなく比較専用。

この3ケース中の最大RSSは、行列積が変更前139020 KiB・採用版150808 KiB・参照153472 KiB、逆行列が変更前151360 KiB・採用版157172 KiB・参照147684 KiB。速度改善と引き換えに、密なケースではメモリが増えている。

時間のばらつきもある。行列積`many_1_00`の変更前は5.82〜11.88秒、採用版は1.45〜2.08秒だった。数%の差を安定した優劣とせず、この6ケースだけで全入力に対して最速とも主張しない。

ブロック化前の逆行列は、公式全件検査の`lowrank_max_random_05`で10秒制限を超えた。[その失敗記録](../benchmarks/results/inverse-matrix-mod2-before-block.json)も保存した。最終版は逆行列37ケース、行列積26ケース、階数35ケース、行列式36ケースをすべて通過した。

生データ: [行列積](../benchmarks/results/matrix-product-mod2-comparison.json)、[逆行列](../benchmarks/results/inverse-matrix-mod2-comparison.json)。追加した他の問題も含む反復測定は[PyPyベンチマーク一覧](../../verify/library_checker/benchmarks/README.md)で確認できる。

```sh
pypy3 library_codex/benchmarks/library_checker.py fetch --problem matrix_product_mod_2 --language pypy3 --top 1 --cache ../lc-matching-reference
pypy3 library_codex/benchmarks/official_comparison.py --snapshot ../lc-matching-reference/matrix_product_mod_2-pypy3.json --reviewed 389256 --problem /home/harurun/.cache/harurun-library-checker/problems/linear_algebra/matrix_product_mod_2 --cases max_random_00 many_1_00 middle_00 --variant baseline=library_codex/benchmarks/baselines/matrix_product_mod_2.py --variant candidate=verify/library_checker/solutions/matrix_product_mod_2.py --repeat 5 --output library_codex/benchmarks/results/matrix-product-mod2-comparison.json
pypy3 library_codex/benchmarks/library_checker.py fetch --problem inverse_matrix_mod_2 --language pypy3 --top 1 --cache ../lc-matching-reference
pypy3 library_codex/benchmarks/official_comparison.py --snapshot ../lc-matching-reference/inverse_matrix_mod_2-pypy3.json --reviewed 389266 --problem /home/harurun/.cache/harurun-library-checker/problems/linear_algebra/inverse_matrix_mod_2 --cases max_fullrank_00 lowrank_max_random_05 perm_max_random_00 --variant baseline=library_codex/benchmarks/baselines/inverse_matrix_mod_2.py --variant candidate=verify/library_checker/solutions/inverse_matrix_mod_2.py --repeat 5 --output library_codex/benchmarks/results/inverse-matrix-mod2-comparison.json
```

### 通常検査の性能変動

同日のPyPy quickテストは124件成功。性能検査の初回は、未変更のCSR Dijkstraだけが速度比0.926倍で基準1.05倍を下回った。コード・基準・入力を変えずに性能検査全体をもう一度実行すると1.233倍で、全項目が基準を通過した。初回の未達は解消を保証できるコード上の不具合と特定しておらず、計測変動として残す。

| CSR Dijkstra測定 | list版の3回（秒） | CSR版の3回（秒） |
| --- | --- | --- |
| 初回 | 0.078569, 0.084105, 0.077810 | 0.091515, 0.076486, 0.084839 |
| 再測定 | 0.086969, 0.075392, 0.084107 | 0.071457, 0.068239, 0.065159 |

これは既存のquick検査が測る構築＋解法の時間であり、上の公式ケース測定とは計測区間が異なる。環境はWSL・Ryzen 7 3700X・PyPy 3.10.14 / 7.3.16。[再測定の全項目の生データ](../benchmarks/results/quick-regression.json)も保存した。

```sh
pypy3 library_codex/tools/run_benchmarks.py --profile quick --output library_codex/benchmarks/results/quick-regression.json
```

## 疎なFPS・二変数FPS・集合冪級数（2026-10-04）

疎なFPSの逆数・exp・log・冪・平方根、二変数FPSの逆数、集合冪級数のexp・log・subset convolutionの9問を追加した。公式revision `1814c4e`の217ケースをすべてPyPyで通過した。オンライン提出はしていない。

測定環境はWSL・AMD Ryzen 7 3700X・PyPy 3.10.14 / 7.3.16。9問それぞれで遅かった公式3ケースを各5回測定し、時間と最大RSSを保存する。全件検証は公式の時間制限を使うが、メモリ制限は強制していない。

本体変更後は依存する5問62ケースを再検証し、全件通過した。専用テスト18件、通常のquickテスト124件、quick性能検査、API・catalog・提出コード同期検査も成功した。全ライブラリのfullテストは今回は再実行していない。

### 疎なFPSの冪

最新問題版のAC・時間昇順で取得したPyPy先頭は[389207 / tyuyu62](https://judge.yosupo.jp/submission/389207)。非零項だけのpair列を受け取って漸化式を計算する。ライブラリ側は既存の`fps_pow`を使い、driverで密な係数listへ変換する。以下はこの入力表現の差・起動・JIT・入出力を含む提出コード全体の比較であり、演算部分だけの比較ではない。

同一の公式入力、WSL・PyPy 3.10.14 / 7.3.16、新規process、順序を入れ替えた5回の中央値。全出力を公式checkerで検査した。

| 公式ケース | 既存版 | 試作版 | 上位PyPy提出 |
| --- | ---: | ---: | ---: |
| max_random_00 | 0.227秒 | 0.231秒 | 0.154秒 |
| small_dense_00 | 0.234秒 | 0.214秒 | 0.167秒 |
| low_deg_zero2_00 | 0.213秒 | 0.235秒 | 0.142秒 |

試作版は疎な冪・平方根の正規化用中間配列を省き、定数倍を漸化式の初期値へ組み込んだ。さらに各積を途中でmodに戻して、大きな中間整数を避けた。3ケース中の最大RSSは既存版141524 KiB、試作版125568 KiB、参照90600 KiB。メモリは減ったが、速度改善が揃わないため本体には採用していない。

[既存版の単独コード](../benchmarks/baselines/sparse_fps_power.py)、[未採用の試作コード](../benchmarks/experiments/sparse_fps_power.py)、[全測定値](../benchmarks/results/sparse-fps-power-comparison.json)を保存した。途中の[配列削減のみの測定](../benchmarks/results/sparse-fps-power-allocation-only.json)も残す。この途中版は試作コードの冪漸化式だけを既存版と同じ式に戻すことで再現できる。

```sh
pypy3 library_codex/benchmarks/library_checker.py fetch --problem pow_of_formal_power_series_sparse --language pypy3 --top 1 --cache ../lc-matching-reference
pypy3 library_codex/benchmarks/official_comparison.py --snapshot ../lc-matching-reference/pow_of_formal_power_series_sparse-pypy3.json --reviewed 389207 --problem /home/harurun/.cache/harurun-library-checker/problems/polynomial/pow_of_formal_power_series_sparse --cases max_random_00 small_dense_00 low_deg_zero2_00 --variant baseline=library_codex/benchmarks/baselines/sparse_fps_power.py --variant candidate=library_codex/benchmarks/experiments/sparse_fps_power.py --repeat 5 --output library_codex/benchmarks/results/sparse-fps-power-comparison.json
```

### 二変数FPSの逆数

公式28ケースを通過した。50万係数までの入力、片方の次数上限が1の入力、縦横に偏った入力を含む。

取得時点の「最新問題版・AC・PyPy3」検索では比較対象を取得できなかった。これは過去の問題版も含めてPyPyのACが存在しないという意味ではない。上位C++23の[400948](https://judge.yosupo.jp/submission/400948)では、切り詰めた二変数積を用いるNewton反復とSIMD NTTを確認した。C++は実行比較していない。[取得条件・revision・source hash](../benchmarks/results/bivariate-fps-inverse-reference.json)を保存した。

### 集合畳み込み

同じ条件のPyPy先頭[389773 / tyuyu62](https://judge.yosupo.jp/submission/389773)を読み、同じ公式入力で5回比較した。参照実装はrankごとの連続配列、ライブラリはmaskごとの連続配列を使う。参照実装はzeta変換後にmodへ戻し、積の各項もmodへ戻している。

| 公式ケース | ライブラリ | 上位PyPy提出 |
| --- | ---: | ---: |
| max_random_00 | 4.717秒 | 2.365秒 |
| random_00 | 4.535秒 | 2.276秒 |
| hack01_00 | 2.374秒 | 2.031秒 |

[各回の時間・RSS・hash](../benchmarks/results/subset-convolution-comparison.json)を保存した。比較範囲では上位実装との差が残る。

続いて、ranked zeta変換後の係数と積の各項をmodへ戻す変更を比較した。PyPyで大きな中間整数へ昇格する計算を減らす。maskごとの配列構成と公開APIは変えていない。

| 公式ケース | 変更前 | 採用版 | 上位PyPy提出 |
| --- | ---: | ---: | ---: |
| max_random_00 | 4.529秒 | 2.748秒 | 2.147秒 |
| random_00 | 4.312秒 | 2.913秒 | 2.119秒 |
| hack01_00 | 2.356秒 | 2.656秒 | 2.148秒 |

大規模ランダム入力2件は約1.48〜1.65倍速くなり、`hack01_00`は約13%遅くなった。重いケースの改善を優先して採用したが、全入力での高速化ではない。3ケース中の最大RSSは変更前588848 KiB、採用版588884 KiB、参照575608 KiBで、メモリ削減はない。上位実装との時間差も残る。

[変更前コード](../benchmarks/baselines/subset_convolution.py)、[測定時の改善案コード](../benchmarks/experiments/subset_convolution_normalized.py)、[各回の測定値](../benchmarks/results/subset-convolution-normalized-comparison.json)を保存した。改善案コードの`multiply`と同じ処理を本体へ反映している。負数・未正規化係数・合成数mod・61 bit modの小入力を単純解と比較する回帰testも追加した。

採用前の反復測定も残している: [subset convolution](../benchmarks/results/subset_convolution-before-normalization.json)、[set exp](../benchmarks/results/exp_of_set_power_series-before-normalization.json)、[set log](../benchmarks/results/log_of_set_power_series-before-normalization.json)。最新の本体に対する記録は[公式ケースのベンチマーク一覧](../../verify/library_checker/benchmarks/README.md)を参照する。

```sh
pypy3 library_codex/benchmarks/library_checker.py fetch --problem subset_convolution --language pypy3 --top 1 --cache ../lc-matching-reference
pypy3 library_codex/benchmarks/official_comparison.py --snapshot ../lc-matching-reference/subset_convolution-pypy3.json --reviewed 389773 --problem /home/harurun/.cache/harurun-library-checker/problems/set_power_series/subset_convolution --cases max_random_00 random_00 hack01_00 --variant library=library_codex/benchmarks/baselines/subset_convolution.py --repeat 5 --output library_codex/benchmarks/results/subset-convolution-comparison.json
pypy3 library_codex/benchmarks/official_comparison.py --snapshot ../lc-matching-reference/subset_convolution-pypy3.json --reviewed 389773 --problem /home/harurun/.cache/harurun-library-checker/problems/set_power_series/subset_convolution --cases max_random_00 random_00 hack01_00 --variant baseline=library_codex/benchmarks/baselines/subset_convolution.py --variant candidate=library_codex/benchmarks/experiments/subset_convolution_normalized.py --repeat 5 --output library_codex/benchmarks/results/subset-convolution-normalized-comparison.json
```

## 数え上げ・集合冪級数の追加検査（2026-10-05）

Bell数・Bernoulli数・分割数、第一種・第二種Stirling数の行と列、集合冪級数の合成・power projectionの9問を追加した。公式revision `1814c4e`の129ケースをすべてPyPyで通過し、累計109問・2439ケースになった。オンライン提出は行っていない。

9問それぞれで公式検査の遅かった3ケースを各5回、計135回再測定した。[問題別の生データと一覧](../../verify/library_checker/benchmarks/README.md)へ保存した。反復測定を保存済みの問題は累計33問で、109問すべてを反復したわけではない。

採用版は専用・関連テスト5件、通常のquickテスト124件、quick性能検査を通過した。全ライブラリのfull検査は今回再実行していない。

Stirling数の列は、Kが0・1・2の専用計算、逆数の重複計算削減、必要な次数までの切り詰めを採用した。K=1・2では約1.7〜2.1秒から0.09〜0.13秒へ短縮したが、一般のKは上位PyPy提出に約2.2〜2.3倍の時間がかかる。[比較条件・全ケースの表・未採用案](STIRLING_BENCHMARK.md)へ記録した。

### 集合冪級数の合成

取得時点の「最新問題版・AC・PyPy3・時間昇順」の先頭は[302939 / kobejean](https://judge.yosupo.jp/submission/302939)。sourceを確認し、同一の公式最大ケースを各5回比較した。WSL・AMD Ryzen 7 3700X・PyPy 3.10.14 / 7.3.16、新規process、起動・JIT・入出力込みの中央値。実行順を入れ替え、全出力を公式checkerで検査した。

| 公式ケース | ライブラリ | 上位PyPy提出 |
| --- | ---: | ---: |
| max_random_00 | 5.913秒 | 3.538秒 |
| max_random_01 | 5.893秒 | 3.726秒 |
| max_random_02 | 5.539秒 | 3.750秒 |

比較範囲では約1.48〜1.67倍の時間がかかる。最大RSSはライブラリ368232 KiB、参照446944 KiBで、ライブラリの方が少ない。sourceと入力のhash、各回の時間・RSSは[結果JSON](../benchmarks/results/set-series-composition-comparison.json)に保存した。

参照実装はrank別の配列と、入力blockのranked zeta変換の再利用を使う。合成の途中結果も変換後の表現で保持している。これは次の改善候補であり、今回の本体には移植していない。時間差の内訳をprofileで特定したわけでもない。

```sh
pypy3 library_codex/benchmarks/library_checker.py fetch --problem polynomial_composite_set_power_series --language pypy3 --top 1 --cache ../lc-matching-reference
pypy3 library_codex/benchmarks/official_comparison.py --snapshot ../lc-matching-reference/polynomial_composite_set_power_series-pypy3.json --reviewed 302939 --problem /home/harurun/.cache/harurun-library-checker/problems/set_power_series/polynomial_composite_set_power_series --cases max_random_00 max_random_01 max_random_02 --variant library=verify/library_checker/solutions/polynomial_composite_set_power_series.py --repeat 5 --output library_codex/benchmarks/results/set-series-composition-comparison.json
```
