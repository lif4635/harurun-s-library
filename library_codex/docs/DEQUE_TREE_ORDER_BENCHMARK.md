# Dequeと木の最小転倒数の検証

2026-10-09 JST。公式revision `1814c4e5205517e368bb57a8d1127eb961cfeaae`の固定ケースで検証した。オンライン提出は行っていない。

## 追加・修正

- `sequence_structure/Deque.py`を追加。両端の追加・削除は償却O(1)、添字による取得・変更はO(1)。二つのlistを使い、最大操作数分の事前確保や要素ごとのnode objectは使わない。
- `ZeroOneTree.min_inversions`と`min_block_inversions`へkeyword-onlyの`return_order=False`を追加。Trueなら`(cost, order)`、省略時は従来どおり整数だけを返す。別名の関数は追加していない。
- `ZeroOneTree`の空の塊を含む入力での不具合を修正。優先度キューを整数IDと位置の配列へ置き換え、古い優先度のobjectを追加し続けない。
- 両moduleの記事、返り値・計算量の説明、単純解との比較testを追加した。

## 見つかった不具合

順序復元を初めに加えた版は、公式`max_bival_00`〜`02`の3ケースでWAになった。失敗を含む[初期検証](../benchmarks/results/tree_inversions_initial_verification.json)と、その[提出コード](../benchmarks/baselines/tree_inversions_before.py)を保存している。

既存の比較器は0/0の塊を他のどの比とも同率とみなし、頂点番号で並べていた。これでは比較の推移性が崩れる。修正版では1の個数が0の塊を先に扱い、それ以外を整数の交差積で比較する。浮動小数点の比は使わない。

小さい再現例:

```python
parent = [0, 0, 1, 0, 3]
zero = [0, 1, 1, 0, 1]
one = [0, 0, 1, 0, 0]
```

旧版の答えは1だが、正解は0。たとえば順序`[0, 1, 3, 4, 2]`ならすべての0が1より先に来る。全順列を調べる単純解でも0を確認し、専用の回帰testへ残した。

## 順序復元と軽量化

各塊を親の塊の直後に結合するとき、末尾と次の頂点を二つの整数配列でつなぐ。最後に根から一度たどるだけで、N頂点の順序を復元できる。return_order=Falseならこの二配列は作らない。

優先度キューは各塊の代表IDを一つだけ保持する。最大の比を持つ塊を親へ結合した後、親の比は下がらないので、その位置から上向きに修正できる。取り消された古い項目や比較用class instanceは不要。

時間はO(N log(N+1) T)、追加メモリはO(N)。Tは重みの整数積・比較のコスト。重みが巨大な整数の場合も厳密に比較する。

## 公式全件検証

| 問題 | 通過ケース |
| --- | ---: |
| deque | 36 |
| rooted_tree_topological_order_with_minimum_inversions | 30 |

追加66ケース。全体は178/253問題・4199ケース通過、未実装75問題。公式の制限時間を使うが、手元のCPU・PyPyはオンライン環境と異なり、メモリ制限は強制していない。

## 測定条件と比較対象

- WSL Ubuntu、Ryzen 7 3700X、PyPy 3.10.14 / 7.3.16。
- 各実装は新しいprocessで5回測定。起動・JIT・入出力を含む壁時計時間の中央値と、最大RSSを記録する。
- 同じ入力・checker・実行環境を使い、実装順をseed固定で入れ替えた。重い検査との同時実行はしていない。
- source・入力・checkerのhashと各回の値をJSONへ残す。
- 木の最適順序は一意でないので、出力文字列の一致ではなく公式checkerで判定する。
- 公式APIから取得時点の最新テストでACのPyPy提出を時間昇順に取得し、全文を確認してから実行した。

比較対象は[Deque 366964](https://judge.yosupo.jp/submission/366964)と[木の順序 301086](https://judge.yosupo.jp/submission/301086)。将来の順位は保証しない。judgeの表示時間とは直接比較しない。

Dequeの参照実装は1000005要素を先に確保する問題専用配列。今回の実装は任意長に伸びる汎用classなので、同じAPI・メモリ構成ではない。木の参照実装は木objectの構築、優先度付きobject、別の優先度キューによる順序復元を含む。下の差は提出全体の差であり、優先度キューだけの倍率ではない。

## 同一入力の比較

時間は秒、RSSはKiB。beforeは今回の最初の順序復元版で、まだ不具合を含む。beforeを測った3ケースは、その版でも公式checkerを通過するケースに限る。不正解の入力を速さの根拠にはしない。

| 問題・ケース | before | 今回 | 上位提出 |
| --- | ---: | ---: | ---: |
| deque max_random_00 | — | 0.1410 | 0.1509 |
| deque max_random_07 | — | 0.1792 | 0.1823 |
| deque max_random_15 | — | 0.1600 | 0.1523 |
| 木 max_random_00 | 1.1155 | 0.5647 | 1.9466 |
| 木 max_typical_tree_00 | 1.4335 | 0.5608 | 1.6309 |
| 木 two_path_02 | 1.2593 | 0.5570 | 1.5334 |
| 木 max_bival_00 | 不正解 | 0.7146 | 1.7128 |
| 木 weight_zero_00 | 未反復 | 0.2362 | 1.1196 |

Dequeは上位提出より約7%速い〜約5%遅い。RSSもケースごとに異なり、全条件で改善したという結果ではない。

木の通常3ケースはbefore比で1.98〜2.56倍速い。上位提出に対して、測定した5ケースでは2.40〜4.74倍速く、RSSは約35〜42%少ない。全入力・全言語で最速になったとは主張しない。

| ケース | before RSS | 今回 RSS | 上位提出 RSS |
| --- | ---: | ---: | ---: |
| deque max_random_00 | — | 70624 | 71676 |
| deque max_random_07 | — | 87100 | 72968 |
| deque max_random_15 | — | 75056 | 71808 |
| 木 max_random_00 | 133244 | 111872 | 187112 |
| 木 max_typical_tree_00 | 147888 | 113464 | 195928 |
| 木 two_path_02 | 146032 | 112888 | 188996 |
| 木 max_bival_00 | — | 121504 | 187980 |
| 木 weight_zero_00 | — | 112420 | 187036 |

- [Deque比較](../benchmarks/results/deque_official_comparison.json)
- [木の通常3ケース](../benchmarks/results/tree_inversions_official_comparison.json)
- [木の重み0を含む2ケース](../benchmarks/results/tree_inversions_zero_comparison.json)

## 通常の反復記録

直前の全件検証で遅かった公式3ケースを各5回測定した結果。上の比較とはケース・実行時刻が異なる。

| 問題 | 中央値の最大 | 最大RSS |
| --- | ---: | ---: |
| deque | 0.1750秒 | 87056 KiB |
| rooted_tree_topological_order_with_minimum_inversions | 0.6867秒 | 120548 KiB |

反復記録は104問題。通過済みの残り74問題には、この形式の反復記録がまだない。

## 保守検査

- Dequeは標準dequeとのランダム比較、両端を交互に動かす列、反転した内部listの再配分、負index、境界、None、表示と浅いコピーを検査する。
- 木は小さい全順列との比較、順序が親子関係を守ること、返した順序のコスト、空の塊、任意の根・番号、巨大な整数、長いパス、不正な親配列を検査する。
- 記事2本の使用例と、単独bundleをcatalogの自動testへ含める。
- PyPyのquick検査は187件通過。今回の専用testはDeque 3件・木6件で、記事とbundleの検査も含む。
- 単独提出・API reference・catalogの同期検査、説明監査、再帰監査が通過。説明監査の検出は0件。
- quick性能退行検査も通過。今回の公式ケースの5回測定とは別に、既存のグラフ・segtree・FPS等の代表ケースを確認した。
- 全178問題の通過記録と104問題の反復記録について、提出コードのhashが現在のファイルと一致することを確認した。比較3記録と初期版2記録も保存コードのhashに一致する。

## 再実行

```sh
pypy3 library_codex/tools/check_library_checker.py test deque rooted_tree_topological_order_with_minimum_inversions --official /home/harurun/.cache/harurun-library-checker/problems --reuse-tests /home/harurun/.cache/online-judge-tools/library-checker-problems
pypy3 library_codex/benchmarks/official_benchmark.py deque rooted_tree_topological_order_with_minimum_inversions --official /home/harurun/.cache/harurun-library-checker/problems --repeat 5 --slowest 3
pypy3 library_codex/tools/prepare_checkpoint.py --profile quick
```

比較対象は`library_codex/benchmarks/library_checker.py fetch --problem NAME --language pypy3 --top 1 --cache ../lc-matching-reference`で取得する。取得時点によって対象IDが変わるため、コードとhashを確認してからreviewedへ指定する。

```sh
pypy3 library_codex/benchmarks/official_comparison.py --snapshot ../lc-matching-reference/deque-pypy3.json --reviewed 366964 --problem /home/harurun/.cache/harurun-library-checker/problems/data_structure/deque --cases max_random_00 max_random_07 max_random_15 --variant library=verify/library_checker/solutions/deque.py --repeat 5 --timeout 90 --output library_codex/benchmarks/results/deque_official_comparison.json
pypy3 library_codex/benchmarks/official_comparison.py --snapshot ../lc-matching-reference/rooted_tree_topological_order_with_minimum_inversions-pypy3.json --reviewed 301086 --problem /home/harurun/.cache/harurun-library-checker/problems/tree/rooted_tree_topological_order_with_minimum_inversions --cases max_random_00 max_typical_tree_00 two_path_02 --variant previous=library_codex/benchmarks/baselines/tree_inversions_before.py --variant library=verify/library_checker/solutions/rooted_tree_topological_order_with_minimum_inversions.py --repeat 5 --timeout 90 --output library_codex/benchmarks/results/tree_inversions_official_comparison.json
pypy3 library_codex/benchmarks/official_comparison.py --snapshot ../lc-matching-reference/rooted_tree_topological_order_with_minimum_inversions-pypy3.json --reviewed 301086 --problem /home/harurun/.cache/harurun-library-checker/problems/tree/rooted_tree_topological_order_with_minimum_inversions --cases max_bival_00 weight_zero_00 --variant library=verify/library_checker/solutions/rooted_tree_topological_order_with_minimum_inversions.py --repeat 5 --timeout 90 --output library_codex/benchmarks/results/tree_inversions_zero_comparison.json
```

full検査、オンライン提出、公開サイトの再デプロイは行っていない。ローカルサイト用のcatalog・コード・ZIPは同期済み。370 moduleのコード1110ファイルとZIP内1377項目がライブラリ側の内容に一致し、ZIPの破損検査も通過した。
