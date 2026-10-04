# データ構造の公式ケース検査と速度比較

2026-10-05 JST。公式revision `1814c4e5205517e368bb57a8d1127eb961cfeaae`、WSL・Ryzen 7 3700X・PyPy 3.10.14 / 7.3.16。オンライン提出は行っていない。

## 追加の高速化と再検査

前回commit `3c1cd37`から区間頻度と動的列を変更した。区間頻度25ケース、区間反転・和20ケース、動的列33ケースを再検査し、78ケースすべて通過した。動的列の前回TLEだった `max_random_00` は7.832秒、全33ケースの最大は `max_random_01` の8.929秒で、10秒制限以内だった。累計は115問題・2586ケース通過、未実装138問題。

### 区間頻度のバケット化

値ごとの出現位置を昇順のバケットへ分け、端の位置は二分探索、途中のバケットは長さを合計する。更新時は分割・隣接結合し、削除済みの位置を蓄積しない。値の大小比較は不要で、辞書のキーにできる値を引き続き扱える。

構築 O(N)、更新・問い合わせ O(sqrt(N+1))、領域 O(N)。辞書操作を O(1) としている。以前の期待 O(log(N+1)) より漸近的には悪いので、すべての入力で速いとはしない。

5回の中央値:

| 公式ケース | 前回版 | 今回版 | 参照234476 |
| --- | ---: | ---: | ---: |
| many_query_0_01 | 3.338秒 | 0.417秒 | 0.481秒 |
| max_03 | 2.282秒 | 0.480秒 | 0.460秒 |
| many_query_1_03 | 0.833秒 | 0.474秒 | 0.413秒 |

前回版比で約1.76〜8.00倍。3ケース中の最大RSSは195740 KiBから134908 KiBへ約31%減った。参照提出比では時間が約0.87〜1.15倍で、メモリは参照の方が小さい。整数へ符号化して1つの集合を持つ参照と異なり、今回は値ごとに位置を持つ。

[前回版](../benchmarks/baselines/point_set_range_frequency_treap.py)と[各回の時間・RSS・hash](../benchmarks/results/point-set-range-frequency-buckets.json)を保存した。

### 動的列の集約領域

`commutative=True` の場合、正順・逆順の集約を同じ配列へ保存し、二重の書込みと交換を省く。既定値のFalseでは別配列のままで、文字列連結などの順序を維持する。

[前回版](../benchmarks/baselines/dynamic_sequence_separate_aggregates.py)と[反復比較](../benchmarks/results/dynamic-sequence-storage-comparison.json)を保存する。最初の1ケース・1回の[試測定](../benchmarks/results/dynamic-sequence-storage-trial.json)は探索用であり、最終比較とは分ける。

5回の中央値:

| 公式ケース | 前回版 | 今回版 | 参照219536 |
| --- | ---: | ---: | ---: |
| max_random_00 | 8.192秒 | 7.513秒 | 6.847秒 |
| max_random_02 | 8.054秒 | 7.303秒 | 6.860秒 |
| max_02 | 7.885秒 | 7.092秒 | 6.318秒 |

前回版から約8〜10%短縮し、3ケース中の最大RSSは225876 KiBから184948 KiBへ約18%減った。参照提出より約6〜12%遅く、同等・最速とはしない。参照の最大RSSは174020 KiB。採否は1回の試測定ではなく、この反復測定と公式全件検査に基づく。

`max_02` は問い合わせ出力がないため、このケース単体のchecker通過だけでは内部状態を検証できない。ほかの公式ケース、非可換演算・遅延作用を含む単純解との比較を併用する。

### 再実行

関連する回帰テスト16件は通過。初回のquick検査では125件通過・1件失敗し、構築計算量がAPI文書では O(N)、catalogでは「実装依存」になっている不一致を検出した。catalog生成器がクラス名の計算量設定を見落としていたため、明示的なconstructor設定がなければクラス名の設定を使うように修正し、複数クラス・個別設定の優先順位を回帰テストへ追加した。

修正後の関連catalogテスト2件は通過。43クラスの構築計算量が既存のAPI設定に一致するようになった。たとえばBITの構築は O(log N) から O(N) へ直る。計算量そのものを43クラス分新しく推測したのではなく、API文書ですでに使っていた設定の取り込みを直している。

共通の生成器も変更したため、full検査へ広げて823件すべて通過した。full性能回帰検査、API文書・catalog・単独コードの同期検査、説明品質検査、再帰監査も通過した。

比較は前回と同じ公式入力、参照source、逐次・新規PyPy processの条件で行う。保存済みJSONに入力・source・checkerのhash、各回の時間とRSSがある。

さらに、変更した3問題で全件検査の遅かった3ケースを各5回測定した。[標準ベンチマーク](../../verify/library_checker/benchmarks/README.md)は累計39問題で、115問題すべてではない。今回の比較90回と標準測定45回、計135回に加え、探索的な3回の測定を保存している。

動的列の標準測定は `max_random_01`、`max_random_00`、`max_random_02` が対象。中央値はそれぞれ7.406秒、7.624秒、7.294秒で、15回中の最大も8.033秒だった。反復測定のtimeoutは公式判定とは別なので、通過判定は先の全33ケース検査に基づく。

```sh
pypy3 library_codex/tools/check_library_checker.py test point_set_range_frequency range_reverse_range_sum dynamic_sequence_range_affine_range_sum --official /home/harurun/.cache/harurun-library-checker/problems
pypy3 library_codex/benchmarks/official_benchmark.py point_set_range_frequency range_reverse_range_sum dynamic_sequence_range_affine_range_sum --official /home/harurun/.cache/harurun-library-checker/problems --repeat 5 --slowest 3
pypy3 library_codex/benchmarks/official_comparison.py --snapshot ../lc-matching-reference/point_set_range_frequency-pypy3.json --reviewed 234476 --problem /home/harurun/.cache/harurun-library-checker/problems/data_structure/point_set_range_frequency --cases many_query_0_01 max_03 many_query_1_03 --variant previous=library_codex/benchmarks/baselines/point_set_range_frequency_treap.py --variant library=verify/library_checker/solutions/point_set_range_frequency.py --repeat 5 --output library_codex/benchmarks/results/point-set-range-frequency-buckets.json
pypy3 library_codex/benchmarks/official_comparison.py --snapshot ../lc-matching-reference/dynamic_sequence_range_affine_range_sum-pypy3.json --reviewed 219536 --problem /home/harurun/.cache/harurun-library-checker/problems/data_structure/dynamic_sequence_range_affine_range_sum --cases max_random_00 max_random_02 max_02 --variant previous=library_codex/benchmarks/baselines/dynamic_sequence_separate_aggregates.py --variant library=verify/library_checker/solutions/dynamic_sequence_range_affine_range_sum.py --repeat 5 --timeout 90 --output library_codex/benchmarks/results/dynamic-sequence-storage-comparison.json
```

## 前回の検証記録（3c1cd37）

以下は今回の変更前の結果。TLEと性能差は当時の状態を残したもので、現在の検証結果は上記のとおり。

### 検証範囲

| 問題 | 公式ケース | 結果 |
| --- | ---: | --- |
| point_set_range_frequency | 25 | 全件通過 |
| double_ended_priority_queue | 18 | 全件通過 |
| persistent_unionfind | 14 | 全件通過 |
| range_reverse_range_sum | 20 | 全件通過 |
| ordered_set | 37 | 全件通過 |
| dynamic_sequence_range_affine_range_sum | 33 | 32通過・1 TLE |

累計114問題・2553ケースが全件通過。未実装138問題と動的列のTLEが残る。動的列の`max_random_00`は10.038秒で打ち切られた。他の測定で10秒未満でも、この全件検査結果を上書きして通過扱いにはしない。

通過した5問題では、各問題の遅かった公式3ケースを5回ずつ計測した。動的列も下記の比較用runnerで最大3ケースを5回ずつ測り、全出力を公式checkerで検査した。ただし比較用timeoutは90秒で、10秒制限の全件検査とは別。

### 比較条件

- 同じ公式入力を使い、各回は新規PyPy process。起動・JIT・入出力を含む時間と最大RSSを記録する。
- 実装の実行順を入れ替え、重いテスト・計測は同時実行しない。
- 参照提出は取得時点の「最新問題版・AC・PyPy3・時間昇順」の先頭。sourceを読んでから実行した。
- 区間頻度は[234476 / Alumite14](https://judge.yosupo.jp/submission/234476)、動的列は[219536 / toyuzuko](https://judge.yosupo.jp/submission/219536)。judge上の秒数と手元の秒数は直接比べない。

### 区間頻度

既存の値へ要素を入れるたびに`TreapSet()`を作って捨てていた処理を除き、出現回数が0になった値の木を辞書から除くようにした。木の内部では削除済みノードを再利用しないため、全体メモリが常に現在の列長だけに比例するわけではない。

APIの計算量表記も、誤っていた O(log² N) から期待 O(log(N+1)) へ修正した。比較実装は、値と位置を1整数に符号化した平方分割の順序付き集合を使う。今回の変更はその方式の移植ではない。

[変更前コード](../benchmarks/baselines/point_set_range_frequency.py)と[反復測定の生データ](../benchmarks/results/point-set-range-frequency-comparison.json)を保存する。

5回の中央値:

| 公式ケース | 変更前 | 採用版 | 上位PyPy提出 |
| --- | ---: | ---: | ---: |
| many_query_0_01 | 3.429秒 | 3.335秒 | 0.483秒 |
| max_03 | 2.500秒 | 2.498秒 | 0.484秒 |
| many_query_1_03 | 0.849秒 | 0.876秒 | 0.422秒 |

この範囲では大きな速度改善はない。最後のケースは約3%遅く、最大RSSも変更前195140 KiBから採用版195800 KiBへ微増した。不要な生成と空の木の保持を避ける変更ではあるが、公式ケースでメモリ削減を実証したわけではない。上位提出との約2.1〜6.9倍の時間差が残り、平方分割方式との比較・採用は次の候補とする。

### 動的列

変更前は33ケース中7件がTLEだった。[変更前の全件結果](../benchmarks/results/dynamic-sequence-before.json)と[変更前コード](../benchmarks/baselines/dynamic_sequence_range_affine_range_sum.py)を保存している。

採用した変更:

- 分割・結合時の経路を、一時的に子ポインタを反転して記録する。
- 挿入・削除・反転・区間更新の分割中は集約の再計算を省き、結合時に修復する。
- 区間積は、木を分割せず境界へ下りながら取得する。
- 優先度を32 bitに収める。ノードの値への作用は、そのノードへ下りるまで遅延させる。
- 可換な集約には`commutative=True`を指定できるようにし、逆順の集約計算を省く。既定値はFalseで、非可換演算を引き続き扱える。
- この問題のdriverではアフィン変換の2係数を1整数へ詰める。ライブラリはtupleなどの任意の作用型も扱う。

参照実装は片方向の集約、整数へ詰めた作用・集約、専用入出力を使う。汎用性と入出力も異なるため、残った時間差を1つの原因だけに帰属させない。[反復比較の生データ](../benchmarks/results/dynamic-sequence-comparison.json)に実装・入力・checkerのhashと各回の時間・RSSを記録する。

5回の中央値:

| 公式ケース | 変更前 | 採用版 | 上位PyPy提出 |
| --- | ---: | ---: | ---: |
| max_random_00 | 18.554秒 | 9.136秒 | 7.470秒 |
| max_random_02 | 17.734秒 | 9.003秒 | 7.572秒 |
| max_02 | 14.635秒 | 9.024秒 | 7.275秒 |

比較範囲では約1.62〜2.03倍速くなった。上位提出に対しては約1.19〜1.24倍の時間がかかる。3ケース中の最大RSSは変更前257704 KiB、採用版226112 KiB、参照173880 KiBで、採用版は変更前から約12%減った。

`max_02`は問い合わせ出力がないため、このケース単体では内部状態の正しさを確認できない。ほかの公式ケースと、挿入・削除・非可換積・反転・アフィン変換・代入の単純解比較を併用している。比較の15回はすべて10秒未満だったが、先の全件検査で1件TLEがあるため、問題全体の状態は`failed`のまま残す。

通常のstack方式へ戻す案も試したが、大入力1回の探索的比較では9.356秒で、採用版の8.547秒より遅かった。この1回だけで全入力の優劣を断定しない。[候補コード](../benchmarks/experiments/dynamic_sequence_standard_merge.py)と[試行結果](../benchmarks/results/dynamic-sequence-merge-trial.json)を残す。

#### 保守時の注意

- 集約を更新しない分割は内部処理専用。右端で分割してから左端で分割し、2回目の探索が使う左部分木のsizeを保つ。
- 結合時は境界上の全ノードを修復する。片側が空だからといって直ちに返すと、古いsize・集約が残る。
- 新たな作用・反転のある境界は、結合前に下ろす。非可換積と遅延代入を組み合わせた回帰testを用意した。
- 保留の有無は`pending`で管理する。未使用の`lazy`を0にしても、作用としての0やNoneと混同しない。

### 比較から除いた提出

`ordered_set`の取得時点のPyPy上位10提出は、Python内へ埋め込んだネイティブ共有ライブラリを読み込む形式だった。先頭は[251590](https://judge.yosupo.jp/submission/251590)。不透明なバイナリは実行せず、純粋なPyPy実装との速度比較にも使っていない。今回の順序付き集合について「最速PyPyと比較済み」とはしない。

### 当時の検査と実行コマンド

この節の比較を再現するときは、3c1cd37時点のsourceを使う。現在のsourceで過去の結果JSONを上書きしない。

今回の関連テスト20件、通常quickテスト126件、quick性能検査は通過した。最後の説明修正後もcatalog・単独コード・説明品質の3件を再検査した。全ライブラリのfull検査は再実行していない。区間反転・和の最終driverにも`commutative=True`を指定し、公式20件と3ケース各5回の測定をやり直している。

今回の通過済み5問題で75回、上位提出を含む2問題の比較で90回の反復測定を保存した。通過済み問題の反復測定は累計38問題で、114問題すべてを反復測定したわけではない。

文書・catalogの生成も検証と同じPyPyで行う。今回、Windows側のCPythonで再生成すると一部の推論表記と一覧に差が出て、PyPyの同期検査が失敗した。生成をPyPyへ揃えて復旧しており、生成器の環境間差そのものは変更していない。

```sh
pypy3 library_codex/tools/check_library_checker.py test point_set_range_frequency double_ended_priority_queue persistent_unionfind range_reverse_range_sum ordered_set dynamic_sequence_range_affine_range_sum --official /home/harurun/.cache/harurun-library-checker/problems
pypy3 library_codex/benchmarks/official_benchmark.py point_set_range_frequency double_ended_priority_queue persistent_unionfind range_reverse_range_sum ordered_set --official /home/harurun/.cache/harurun-library-checker/problems --repeat 5 --slowest 3
pypy3 library_codex/benchmarks/library_checker.py fetch --problem point_set_range_frequency --language pypy3 --top 1 --cache ../lc-matching-reference
pypy3 library_codex/benchmarks/library_checker.py fetch --problem dynamic_sequence_range_affine_range_sum --language pypy3 --top 1 --cache ../lc-matching-reference
pypy3 library_codex/benchmarks/official_comparison.py --snapshot ../lc-matching-reference/point_set_range_frequency-pypy3.json --reviewed 234476 --problem /home/harurun/.cache/harurun-library-checker/problems/data_structure/point_set_range_frequency --cases many_query_0_01 max_03 many_query_1_03 --variant baseline=library_codex/benchmarks/baselines/point_set_range_frequency.py --variant library=verify/library_checker/solutions/point_set_range_frequency.py --repeat 5 --output library_codex/benchmarks/results/point-set-range-frequency-comparison.json
pypy3 library_codex/benchmarks/official_comparison.py --snapshot ../lc-matching-reference/dynamic_sequence_range_affine_range_sum-pypy3.json --reviewed 219536 --problem /home/harurun/.cache/harurun-library-checker/problems/data_structure/dynamic_sequence_range_affine_range_sum --cases max_random_00 max_random_02 max_02 --variant baseline=library_codex/benchmarks/baselines/dynamic_sequence_range_affine_range_sum.py --variant library=verify/library_checker/solutions/dynamic_sequence_range_affine_range_sum.py --repeat 5 --timeout 90 --output library_codex/benchmarks/results/dynamic-sequence-comparison.json
```

参照のランキングは変化する。再取得時に対象IDが変わった場合、保存済みJSONのID・source hashと一致するsourceを取得・確認してから比較する。
