# 区間代入と巨大配列の検証

2026-10-09 JST。公式revision `1814c4e5205517e368bb57a8d1127eb961cfeaae`の固定ケースを使う。オンライン提出は行わない。

## 追加したもの

- `RangeAssignSegTree(op, identity, values)`。区間代入、モノイドの区間積、一点更新・取得、デバッグ表示を備える。mapping・compositionは利用者へ要求しない。
- `point_set_range_composite_large_array`のdriver。初期値が恒等関数なので、更新される座標だけを圧縮し、既存のSegTreeを使う。
- `range_affine_range_sum_large_array`のdriver。更新・問い合わせの端点を圧縮し、既存のLazySegTreeで処理する。圧縮後の葉数と元の座標幅を区別し、集計値に幅を持たせる。
- `range_set_range_composite`のdriver。新しいRangeAssignSegTreeへ一次関数の合成演算を渡す。
- SegTreeとLazySegTreeの記事。非可換演算の順番、圧縮した区間の幅、返り値の読み方を実行例で説明する。

通常のSegTree・LazySegTreeのsourceとAPIは変更していない。初めの2問の最適化はdriverのデータ表現・入出力の変更であり、一般用途のセグ木全体が同じ倍率で速くなったという意味ではない。

## 区間代入の実装

代入値xの1個・2個・4個分の積を、更新の走査に合わせて作る。各段は積と一つ下の段への参照を持つ。子へ保留中の代入を反映するときは下の段の積を使うだけで、opを再計算しない。

高さhのnodeが保持するのは高々h+1段。古い更新の表を別に全保存せず、現在のnodeから到達できる段だけが残る。木全体の高さの和がO(N)なので、生存する値と参照の個数もO(N)。値そのものの大きさやPyPyのGC領域を定数とはみなさない。

構築はO(N)回、assign・prodはO(log N)回のopを使う。get・tolistの伝播ではopを呼ばない。値がNoneでも扱え、非可換な場合は左から右の順序を守る。

## 初期実装と失敗

最初は3問とも既存のSegTree/LazySegTreeへ係数tupleを渡した。巨大配列の2問は通過したが、区間上書きは23ケース中5ケースでTLE。

係数を整数に詰めた中間版ではTLEが2ケースへ減ったが、制限時間5秒を超えた。RangeAssignSegTreeへ置き換えた最終版は全23ケースを通過した。

比較用のbeforeは今回作った最初のdriverで、以前から同じ問題が対応済みだったという意味ではない。

- [関数合成の初期検証](../benchmarks/results/point_set_range_composite_large_array_initial_verification.json)
- [affine更新の初期検証](../benchmarks/results/range_affine_range_sum_large_array_initial_verification.json)
- [区間上書きの初期検証](../benchmarks/results/range_set_range_composite_initial_verification.json)
- [整数化だけの中間検証](../benchmarks/results/range_set_range_composite_packed_verification.json)

係数や集計値は30ビットずつ詰める。この表現は公式の法998244353、座標幅10^9以下の制約に依存する。汎用classにはその制限を持ち込まない。係数0・1も単純解testに含めた。定数の手入力で誤ったシフト済み法は単純解testが検出し、`998244353 << 30`という式へ修正した。

## 公式全件検証

| 問題 | 通過ケース |
| --- | ---: |
| point_set_range_composite_large_array | 25 |
| range_affine_range_sum_large_array | 31 |
| range_set_range_composite | 23 |

追加79ケース。全体は176/253問題・4133ケース通過、未実装77問題。

## 測定条件

- WSL Ubuntu、Ryzen 7 3700X、PyPy 3.10.14 / 7.3.16。
- 新しいprocessを毎回起動し、入出力・JIT込みの壁時計時間を5回測定して中央値を取る。
- 重い検査や他の測定とは同時実行しない。実装順はseed固定で入れ替える。
- 出力を公式checkerで検証し、source・入力・checkerのhash、各回の時間、最大RSSを保存する。
- 最大RSSはPyPy本体・入出力を含む。メモリ制限の強制ではない。
- 通常benchmarkは直前の全件検証で遅かった3ケースのみを反復する。全公式ケースを5回ずつ測ったわけではない。

## 比較対象

2026-10-09 JSTに公式APIから最新テストでACのPyPy提出をjudge時間昇順で取得し、全文を確認してから実行する。

- [Point Set Range Composite 391756](https://judge.yosupo.jp/submission/391756)
- [Range Affine Range Sum 391761](https://judge.yosupo.jp/submission/391761)
- [Range Set Range Composite 216575](https://judge.yosupo.jp/submission/216575)

前二つはofflineの圧縮セグ木、最後は上書きごとに繰り返し二乗の表を保存する遅延セグ木。judgeに表示される時間とローカルの時間を直接比べない。比較対象の順位は取得時点のもので、将来も最速であるとは限らない。

## 同一入力での比較

時間は5回の中央値。各欄は秒 / 最大RSS（MiB）。beforeはこの作業内の初期実装、referenceは上記の提出。RSSは5回の最大値で、中央値を出した回と同じとは限らない。

### 巨大配列の一点更新・関数合成

| ケース | before | 今回 | reference |
| --- | ---: | ---: | ---: |
| max_random_00 | 1.464 / 203.9 | 0.909 / 127.6 | 0.739 / 153.2 |
| small_N_00 | 0.339 / 131.3 | 0.313 / 108.1 | 0.251 / 137.6 |
| query_0_then_1_00 | 1.365 / 195.6 | 0.822 / 127.2 | 0.698 / 142.3 |

before比で1.08〜1.66倍速い。referenceより18〜24%遅いが、最大RSSは小さい。セグ木本体を問題専用に複製せず、既存のSegTreeを使っている。

入力を一括でsplitした中間版は0.427〜1.001秒、272.9〜279.2 MiBだった。行ごとに読み、整数を一つの平坦なlistへ格納すると、今回の3ケースすべてで時間・メモリが改善した。中間版のsourceと最初の比較も残す。

一括入力版は最初の測定hashと一致するsourceを復元して保存した。途中で比較用コピーのdocstringが文字化けしたため、正常なsourceで最終比較を再実行した。上表と最終JSONは再実行後の値。

### 巨大配列のaffine更新・区間和

| ケース | before | 今回 | reference |
| --- | ---: | ---: | ---: |
| max_random_00 | 1.355 / 173.1 | 0.831 / 109.8 | 0.657 / 107.8 |
| small_N_00 | 0.120 / 76.1 | 0.122 / 76.0 | 0.124 / 88.4 |
| near_0_and_N_00 | 0.902 / 127.6 | 0.694 / 98.9 | 0.505 / 91.0 |

大きい2ケースはbefore比で1.30〜1.63倍速い。small_Nでは差が小さく、約2%遅くなった。referenceに対して大きい2ケースは26〜37%遅く、RSSも約2〜9%多い。既存LazySegTreeの汎用APIを維持したdriverであり、最速になったという結果ではない。

### 区間上書き・関数合成

| ケース | before | 整数化したLazySegTree | 今回 | reference |
| --- | ---: | ---: | ---: | ---: |
| max_random_00 | 5.429 / 296.8 | 3.625 / 157.2 | 1.924 / 129.9 | 2.149 / 191.3 |
| slide_window_00 | 3.706 / 258.4 | 2.281 / 141.8 | 1.475 / 121.8 | 1.866 / 199.5 |
| fragment_00 | 3.019 / 233.3 | 1.601 / 133.4 | 1.249 / 118.3 | 1.702 / 189.0 |

before比で2.42〜2.82倍、整数化だけの中間版比でも1.28〜1.88倍速い。referenceより時間は10〜27%短く、RSSは32〜39%少ない。これは測定した3ケースの結果で、全入力で最速であるとは主張しない。

- [一点更新の比較記録](../benchmarks/results/point_composite_large_official_comparison.json)
- [一括入力版の最初の比較記録](../benchmarks/results/point_composite_large_bulk_comparison.json)
- [affine更新の比較記録](../benchmarks/results/affine_large_official_comparison.json)
- [区間上書きの比較記録](../benchmarks/results/range_assign_official_comparison.json)

## 通常の反復ベンチマーク

直前の全件検証で遅かった3ケースを各5回測定した結果。上の比較とは選択ケースと実行時刻が異なる。

| 問題 | 中央値の最大 | 最大RSS |
| --- | ---: | ---: |
| point_set_range_composite_large_array | 0.960秒 | 151172 KiB |
| range_affine_range_sum_large_array | 0.903秒 | 112548 KiB |
| range_set_range_composite | 2.074秒 | 133668 KiB |

[問題別の反復記録](../../verify/library_checker/benchmarks/README.md)は102問題。通過済みの残り74問題には、この形式の反復記録がまだない。

## 単体検査

- 関連7テスト通過。新classの4件、3問のdriverと単純解の比較3件。
- 非可換な関数合成、係数0・1、非2冪長、空区間、Noneの値、範囲外、上書き後のget・tolist・str・reprを検査する。
- 連続した上書きで保持するpower tagが増え続けないことを専用testで確認する。
- 3記事のPython使用例5個をcatalogの自動testへ追加した。
- 通常のquick検査177テスト通過。提出用コード・API・catalogの同期検査、説明監査（指摘0件）、再帰監査も通過した。
- quick性能回帰検査も通過。今回の公式ケース比較とは別の、通常保守用の検査。
- 既存の通過記録176問と反復記録102問すべてについて、現在の提出コードのhashとの一致を確認した。

## 再実行

```sh
pypy3 library_codex/tools/check_library_checker.py test point_set_range_composite_large_array range_affine_range_sum_large_array range_set_range_composite --official /home/harurun/.cache/harurun-library-checker/problems --reuse-tests /home/harurun/.cache/online-judge-tools/library-checker-problems
pypy3 library_codex/benchmarks/official_benchmark.py point_set_range_composite_large_array range_affine_range_sum_large_array range_set_range_composite --official /home/harurun/.cache/harurun-library-checker/problems --repeat 5 --slowest 3
pypy3 -m pytest -q library_codex/verify/segment_tree/test_range_assign_segtree.py library_codex/verify/test_official_library_checker.py -k 'range_assign or affine_drivers or noncommutative_affine or none_values or power_tags'
pypy3 library_codex/tools/prepare_checkpoint.py --profile quick
```

比較対象を再取得する場合は、各problemについて`library_codex/benchmarks/library_checker.py fetch --problem NAME --language pypy3 --top 1 --cache ../lc-matching-reference`を使う。順位は変わり得るので、snapshotの提出ID・source・hashを確認してからreviewedへ渡す。記録内には今回のsnapshotも保存している。

```sh
pypy3 library_codex/benchmarks/official_comparison.py --snapshot ../lc-matching-reference/point_set_range_composite_large_array-pypy3.json --reviewed 391756 --problem /home/harurun/.cache/harurun-library-checker/problems/data_structure/point_set_range_composite_large_array --cases max_random_00 small_N_00 query_0_then_1_00 --variant previous=library_codex/benchmarks/baselines/point_set_range_composite_large_array_before.py --variant bulk=library_codex/benchmarks/baselines/point_set_range_composite_large_array_bulk.py --variant library=verify/library_checker/solutions/point_set_range_composite_large_array.py --repeat 5 --timeout 90 --output library_codex/benchmarks/results/point_composite_large_official_comparison.json
pypy3 library_codex/benchmarks/official_comparison.py --snapshot ../lc-matching-reference/range_affine_range_sum_large_array-pypy3.json --reviewed 391761 --problem /home/harurun/.cache/harurun-library-checker/problems/data_structure/range_affine_range_sum_large_array --cases max_random_00 small_N_00 near_0_and_N_00 --variant previous=library_codex/benchmarks/baselines/range_affine_range_sum_large_array_before.py --variant library=verify/library_checker/solutions/range_affine_range_sum_large_array.py --repeat 5 --timeout 90 --output library_codex/benchmarks/results/affine_large_official_comparison.json
pypy3 library_codex/benchmarks/official_comparison.py --snapshot ../lc-matching-reference/range_set_range_composite-pypy3.json --reviewed 216575 --problem /home/harurun/.cache/harurun-library-checker/problems/data_structure/range_set_range_composite --cases max_random_00 slide_window_00 fragment_00 --variant previous=library_codex/benchmarks/baselines/range_set_range_composite_before.py --variant packed=library_codex/benchmarks/baselines/range_set_range_composite_packed.py --variant library=verify/library_checker/solutions/range_set_range_composite.py --repeat 5 --timeout 90 --output library_codex/benchmarks/results/range_assign_official_comparison.json
```

今回full検査、オンライン提出、公開サイトの再デプロイは行っていない。ローカルのサイト用catalog・コード・ZIPは検査後に同期する。
