# グラフ列挙・Steiner木・chordal判定の検証

2026-10-09 JST。公式revision `1814c4e5205517e368bb57a8d1127eb961cfeaae`を固定し、オンライン提出は行っていない。

## 公式全件検証

| 問題 | ケース数 | 使用するmodule |
| --- | ---: | --- |
| chromatic_number | 26 | ChromaticNumber、exact=True |
| enumerate_cliques | 23 | EnumerateCliques |
| maximum_independent_set | 16 | MaximumIndependentSet |
| counting_c4 | 29 | CountC4PerEdge |
| minimum_steiner_tree | 24 | MinimumSteinerTree |
| chordal_graph_recognition | 22 | GraphProperties |

追加140ケース。累計184/253問題・4339ケース通過、未実装69問題。手元では公式の時間制限を使うが、オンラインとはCPU・PyPyが異なる。メモリ制限は強制していない。

## 修正内容

### 多重辺を含む4-cycle

既存実装は単純グラフ専用で、公式の多重辺サンプル1件がWA、平行辺の多い7件が10秒でTLEになった。失敗を含む[初期検証](../benchmarks/results/counting_c4_initial_verification.json)と[その提出コード](../benchmarks/baselines/counting_c4_initial.py)を保存した。

平行辺を重みの和にまとめ、単純グラフ上で計算した後、元の辺番号へ答えを戻す。同じ閉路に平行な2辺を同時に選ばないため、この集約で各元辺の答えを復元できる。対象辺自身の重みは掛けないので、0や負数、平行辺の重みの相殺も扱える。

修正後は全29ケース通過。多重辺の処理は高速になったが、単純グラフには集約の時間・メモリが加わる。下の比較にもこの負担を含める。

### Steiner木

指定頂点を一つ、最後の到達先へ固定する。部分集合DPに含める指定頂点はK-1個になり、状態数は半分、集合分割の項は3^Kから3^(K-1)になる。全指定頂点・終点の表を返すsteiner_tree_dpは契約どおり全状態を保持する。

最小辺集合の復元情報はtupleから整数一つへ変更した。負数は集合分割、正数は直前の辺番号、0は開始状態。辺の向きは復元先の頂点と元の端点から判定する。入力の親子objectや再帰は使わない。

### Chordal判定

MCSの次数別bucketをsetの配列から、前後の頂点IDを持つ整数配列へ変更した。隣接先もsetを常駐させずlistで保持する。除去順の検査は、親候補ごとにまとめた照会と頂点のmarkで行う。

入力はdriverで行ごとに読み、判定器へ渡した後の元の隣接listを解放する。したがって下の比較は構造だけでなく、提出全体のメモリ改善を含む。最適順序や誘導閉路の選び方は変わり得るが、公式checkerで有効性を確認する。

### そのまま採用した実装

彩色数・全クリーク列挙・最大独立集合は、既存アルゴリズムのまま全件通過した。今回追加したのは公式driver、反復測定、専用test、記事とAPI説明。

彩色数のdriverはexact=Trueを使う。参照提出は剰余による判定なので厳密性の条件が異なるが、library側を弱い条件へ変更して速く見せてはいない。最大独立集合の参照提出は再帰版、libraryは反復版。

## 比較条件

- WSL Ubuntu、Ryzen 7 3700X、PyPy 3.10.14 / 7.3.16。
- 全実装を同じ公式入力・checker・PyPyで各5回実行する。各回は新規processで、起動・JIT・入出力を含む壁時計時間。順序はseed固定で入れ替える。
- 重いテストと並行させず、最大RSSも記録する。Windowsの他アプリやCPU周波数は固定していない。
- source、入力、checkerのhashと各回の値はJSONへ保存する。非一意の出力は文字列比較ではなく公式checkerを使う。
- 公式APIから、取得時点で最新テストACのPyPy提出を時間昇順で取得し、全文確認してから実行した。後日の順位や全言語での最速性は保証しない。
- beforeは今回の変更前の提出コード。C4のbeforeを測るのは、正答できる単純グラフ3ケースだけ。不正解・TLEを通常の速度比へ混ぜない。
- 初期全件検証のsourceはbaselinesの`*_initial.py`、比較測定の変更前sourceは`*_before.py`。Windows PythonとPyPyのAST整形差だけがあり、各記録に対応するhashのまま両方保存した。
- 上位C4提出は手元の完全グラフで中央値が10秒を超えた。比較時は90秒の打切り時間を使い、checkerの正答と公式時間内の通過を区別する。

比較元: [彩色数45019](https://judge.yosupo.jp/submission/45019)、[クリーク198016](https://judge.yosupo.jp/submission/198016)、[独立集合389034](https://judge.yosupo.jp/submission/389034)、[C4 334905](https://judge.yosupo.jp/submission/334905)、[Steiner木282060](https://judge.yosupo.jp/submission/282060)、[chordal判定230949](https://judge.yosupo.jp/submission/230949)。

## 同一入力の比較

時間は秒の中央値、RSSはKiB。各行5回。beforeがない欄は測定していない。

| 問題・ケース | before 秒 | 今回 秒 | 上位提出 秒 | before RSS | 今回 RSS | 上位提出 RSS |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| chromatic_number / big_02 | — | 0.1004 | 0.3700 | — | 68780 | 110456 |
| chromatic_number / big_08 | — | 0.1103 | 0.2516 | — | 69328 | 110448 |
| chromatic_number / clique_cycle_03 | — | 0.0993 | 0.6614 | — | 68928 | 110440 |
| enumerate_cliques / large_sparse_00 | — | 0.0781 | 0.0775 | — | 61092 | 61300 |
| enumerate_cliques / max_complete_00 | — | 0.0732 | 0.0755 | — | 61096 | 61296 |
| enumerate_cliques / star_00 | — | 0.0638 | 0.0772 | — | 59888 | 61164 |
| maximum_independent_set / hack0_00 | — | 0.0609 | 0.0647 | — | 59876 | 59876 |
| maximum_independent_set / many_maximals_00 | — | 0.0643 | 0.0603 | — | 59892 | 59888 |
| maximum_independent_set / max_random_04 | — | 0.0676 | 0.0698 | — | 60028 | 60204 |
| counting_c4 / max_complete_00 | 3.9135 | 4.0830 | 10.1441 | 137716 | 170968 | 425216 |
| counting_c4 / max_random_simple_00 | 0.6226 | 0.8406 | 3.2090 | 168280 | 190368 | 308528 |
| counting_c4 / star_00 | 0.3351 | 0.5425 | 2.8164 | 166212 | 201664 | 353524 |
| counting_c4_parallel / multiplied_c4_00 | — | 0.3055 | 0.4542 | — | 136836 | 152580 |
| counting_c4_parallel / dense_00 | — | 0.2332 | 0.2206 | — | 121468 | 103968 |
| minimum_steiner_tree / random_max_00 | 0.7034 | 0.4334 | 0.7916 | 86188 | 67956 | 85716 |
| minimum_steiner_tree / random_complete_00 | 0.3737 | 0.2468 | 0.4786 | 73824 | 66108 | 74916 |
| minimum_steiner_tree / overflow_killer_00 | 0.8995 | 0.3238 | 0.7504 | 91500 | 69024 | 87740 |
| chordal_graph_recognition / path_00 | 1.0297 | 0.9898 | 0.8771 | 202620 | 128132 | 145492 |
| chordal_graph_recognition / cycle_00 | 1.0750 | 1.0253 | 1.0004 | 218760 | 144404 | 153188 |
| chordal_graph_recognition / random_01 | 0.9622 | 0.9651 | 0.9016 | 197724 | 129032 | 141064 |
| chordal_graph_recognition / 2tree_00 | 0.6066 | 0.5225 | 0.6714 | 146744 | 103100 | 128608 |
| chordal_graph_recognition / complete_minus_ab_cd_00 | 0.1851 | 0.1571 | 0.3072 | 101640 | 89484 | 118152 |

- 彩色数は既存の厳密版で、上位提出より約2.3〜6.7倍速かった。今回新たに高速化した倍率ではない。
- クリーク列挙・最大独立集合は上位提出とほぼ同程度。短い実行時間のため、数msの差を一般的な優劣とは扱わない。
- C4は上位提出より単純グラフ3ケースで約2.5〜5.2倍速い。一方、単純グラフ専用だったbeforeより約4〜62%遅く、メモリも増えた。多重辺に対応するための集約コストであり、全条件で改善したわけではない。多重辺dense_00では上位提出のほうが少し速く、メモリも少ない。
- Steiner木はbefore比で約1.5〜2.8倍高速、最大RSSは約10〜25%減。上位提出比では約1.8〜2.3倍高速。
- Chordal判定はbefore比で実行時間がほぼ同等〜約15%短縮、最大RSSは約12〜37%減。上位提出に対しては入力によって速い・遅いが分かれる。

生データ:

- [chromatic_number](../benchmarks/results/chromatic_number_official_comparison.json)
- [enumerate_cliques](../benchmarks/results/enumerate_cliques_official_comparison.json)
- [maximum_independent_set](../benchmarks/results/maximum_independent_set_official_comparison.json)
- [counting_c4](../benchmarks/results/counting_c4_official_comparison.json)
- [counting_c4_parallel](../benchmarks/results/counting_c4_parallel_official_comparison.json)
- [minimum_steiner_tree](../benchmarks/results/minimum_steiner_tree_official_comparison.json)
- [chordal_graph_recognition](../benchmarks/results/chordal_graph_recognition_official_comparison.json)

通常の反復記録は110問題分。全件通過済みの残り74問題には、この形式の反復記録がまだない。

## 保守検査の内容

- 既存の一括testから6 moduleのtestを専用fileへ分離した。もとの単純解比較は残す。
- C4は4辺の全組合せとの比較、多重辺・逆向きの平行辺・負数・0・相殺・入力不変性を検査する。
- Steiner木は辺部分集合の全列挙、指定頂点の順序と重複、0重み、多重辺、任意精度整数、非連結、全表の各状態を検査する。
- Chordal判定は小グラフの誘導閉路全探索、長いパスと閉路、返したlistを変更してもcacheが壊れないことを検査する。
- 6記事の使用例を、通常importと単独bundleの両方で実行する。各APIの返り値と計算量もmetadataへ明記した。

## 最終検査

- PyPyのfull testは955件すべて通過。byte-compile、提出コード・API・catalogの同期検査、説明監査も通過した。
- 再帰監査は6093関数を確認し、直接・相互再帰とも0件。
- full性能回帰検査も通過。これは既定workloadの速度比とchecksumの検査であり、すべての入力で高速化したことを意味しない。
- 累計184問題の公式結果について4339ケースがACであること、現行提出コードとsource hashが一致することを確認した。この回に公式全件を再実行したのは上記6問題。
- 5回測定済み110問題の記録も現行提出コードと一致する。今回の比較7記録と初期検証3記録は、それぞれの現行・変更前・初期sourceへ対応付けて照合した。
- ローカルのサイト用catalogは370モジュール、コピー用コードは1110ファイル。ZIP内1405ファイルもすべて正本とbyte単位で照合した。公開サイトの再デプロイは行っていない。

full検査後はREADMEの検証件数を更新し、catalogを再生成して同期検査を通した。6記事の使用例も再検査した。実装と測定対象コードは変更していない。

## 再実行

```sh
pypy3 library_codex/tools/check_library_checker.py test chromatic_number enumerate_cliques maximum_independent_set counting_c4 minimum_steiner_tree chordal_graph_recognition --official /home/harurun/.cache/harurun-library-checker/problems --reuse-tests /home/harurun/.cache/online-judge-tools/library-checker-problems
pypy3 library_codex/benchmarks/official_benchmark.py chromatic_number enumerate_cliques maximum_independent_set counting_c4 minimum_steiner_tree chordal_graph_recognition --official /home/harurun/.cache/harurun-library-checker/problems --repeat 5 --slowest 3
pypy3 library_codex/tools/prepare_checkpoint.py --profile full
```

比較はofficial_comparison.pyへ各記録のsnapshot・reviewed ID・caseを指定する。snapshot取得後はsourceのhashと内容を確認し、未確認の取得コードは実行しない。外部提出のコードはリポジトリへ複製しない。
