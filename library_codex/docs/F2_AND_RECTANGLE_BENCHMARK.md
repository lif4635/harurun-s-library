# F₂の連立方程式・空間交差と長方形の面積

2026-10-07。Library Checker公式revision `1814c4e5205517e368bb57a8d1127eb961cfeaae`。
オンライン提出は行わない。

## 今回の変更

- `F2Matrix.solve(b)`を追加した。解を一つ表す整数と、零空間の基底を表す整数listを返す。解なしはNone。元の行列は変更しない。
- 大きい行列の`sweep`を8列ずつまとめた消去へ変更した。幅・階数が8の倍数でない行列、自由変数が途中にある行列にも対応する。
- `XorBasis.intersection(other)`を追加した。両方で作れる整数の共通部分を、新しいXorBasisとして返す。
- XorBasisのconstructorは、初期値の追加ごとではなく最後にまとめて簡約する。同じ簡約基底同士の共通部分はコピーだけで返す。
- 長方形の面積は、探索タプルを積む更新から反復区間木へ変更した。両軸を圧縮し、区間数が少ない軸を区間木に使う。イベントはhead・next・端点の平坦な整数配列で保持する。
- XorBasis・UnionRectangleに`tolist`・`str`・`repr`を追加した。XorBasisで表示するのは独立な基底であり、表現できる値すべてではない。
- XorBasisの`rank`が空間の次元のように読める説明と、O(1)という誤った計算量を修正した。返すのは作れる値の昇順での位置。通常の検索と同じく基底数に比例する。

## 公式検証

| 問題 | 公式ケース |
| --- | ---: |
| area_of_union_of_rectangles | 21 |
| system_of_linear_equations_mod_2 | 36 |
| intersection_of_f2_vector_spaces | 17 |

追加74ケースと、既存のF2Matrixを使う逆行列37、行列式36、行列積26、階数35ケースがすべて通過した。全体は173/253問題・4054ケース通過、未実装80問題、古い公式検証結果0件。

最初の実装では面積計算の14/21ケース、連立方程式の7/36ケースがTLEだった。面積計算は区間木だけを反復化した段階でも7ケースがTLEで、イベント表現と走査軸も変えた。

- [面積計算の最初の検証](../benchmarks/results/area_of_union_of_rectangles_initial_verification.json)
- [反復区間木のみの検証](../benchmarks/results/area_of_union_of_rectangles_iterative_verification.json)
- [1列ずつ消去した連立方程式の検証](../benchmarks/results/system_of_linear_equations_mod_2_initial_verification.json)

これらのJSONと対応する`benchmarks/baselines/*_before.py`・`area_of_union_of_rectangles_iterative.py`を残した。失敗した結果を、成功した最終結果として数えない。

連立方程式・空間交差のbeforeは、今回新しく追加した最初のAPI実装。追加前のライブラリに同じAPIがあったという意味ではない。面積計算のbeforeは既存の実装。

## 測定条件

- WSL Ubuntu、AMD Ryzen 7 3700X、PyPy 3.10.14 / 7.3.16。
- 新しいPyPyプロセスで各ケース5回。JIT・起動・入出力込みの壁時計時間の中央値。
- 実装順を入れ替え、重い検査と測定を同時実行しない。
- 出力は公式checkerで検査する。解や基底が一意でない問題も、文字列の一致では判定しない。
- source・入力・checkerのhash、各回の時間、最大RSSをJSONへ保存する。RSSはプロセス全体の値で、メモリ制限を強制した結果ではない。

## 最終版の通常ベンチマーク

公式全件検証で遅かった3ケースを各5回測定した。全ケースを反復したわけではない。

| 問題 | 最大中央値 | 最大RSS |
| --- | ---: | ---: |
| area_of_union_of_rectangles | 3.142秒 | 428572 KiB |
| system_of_linear_equations_mod_2 | 1.393秒 | 108252 KiB |
| intersection_of_f2_vector_spaces | 2.225秒 | 123816 KiB |
| inverse_matrix_mod_2 | 2.268秒 | 156488 KiB |
| matrix_det_mod_2 | 0.449秒 | 67576 KiB |
| matrix_product_mod_2 | 1.938秒 | 150944 KiB |
| matrix_rank_mod_2 | 1.501秒 | 323224 KiB |

[問題別の反復記録](../../verify/library_checker/benchmarks/README.md)は99問題になった。通過済みの残り74問題には、この形式の反復記録がまだない。

## 比較対象

最新テストでACのPyPy提出をjudge時間昇順で取得し、コードの内容を確認してから同じ入力・環境で実行する。judge上の表示時間とローカル時間を直接比較しない。

- [長方形の面積 394104](https://judge.yosupo.jp/submission/394104)
- [F₂連立方程式 389265](https://judge.yosupo.jp/submission/389265)
- [F₂空間交差 205851](https://judge.yosupo.jp/submission/205851)

前二つの平坦な区間木・8列消去を参考に、既存のAPIと整数ビット列の表現を保って実装した。空間交差は[公式の消去法](https://github.com/yosupo06/library-checker-problems/blob/1814c4e5205517e368bb57a8d1127eb961cfeaae/linear_algebra/intersection_of_f2_vector_spaces/intersection.h)も参照し、一方の空間で消した成分を追跡する。

## 同一入力での比較

時間は5回の中央値。beforeは上記の保存した実装、referenceは各問題の比較対象。

| 問題・ケース | before | 今回 | reference |
| --- | ---: | ---: | ---: |
| 面積 max_random_00 | 9.796秒 | 3.178秒 | 2.742秒 |
| 面積 edge_bound_00 | 7.542秒 | 2.763秒 | 2.374秒 |
| 連立方程式 max_random_00（解なし） | 5.141秒 | 1.378秒 | 1.427秒 |
| 連立方程式 max_lowrank_03（解なし） | 1.598秒 | 1.111秒 | 1.035秒 |
| 連立方程式 max_lowrank_00（基底4095本） | 0.591秒 | 0.616秒 | 0.791秒 |
| 連立方程式 max_lowrank_04（基底96本） | 5.072秒 | 1.423秒 | 1.398秒 |
| 空間交差 max_random_00 | 2.865秒 | 1.912秒 | 2.242秒 |
| 空間交差 max_minus_1_random_00 | 2.795秒 | 2.242秒 | 2.168秒 |
| 空間交差 nmk_all_00 | 1.294秒 | 1.106秒 | 1.057秒 |

面積は既存実装の2.73〜3.08倍速くなったが、referenceより約16%遅い。最大RSSも415464〜417636 KiBで、beforeの389028〜390008 KiB、referenceの346736〜355892 KiBより多い。速度と引き換えにメモリが増えた点は残っている。

空間交差はbeforeの1.17〜1.50倍。referenceに対してはケースにより約15%速い〜約5%遅い。最大RSSは93144〜125208 KiBで、referenceより多い。すべての入力で最速になったという結果ではない。

連立方程式は、最初の比較2ケースがどちらも解なしだったため、解と零空間の基底を復元する2ケースも追加した。階数4000ではbeforeの3.57倍、階数1では約4%遅くなった。基底4095本のケースでは、referenceの261872 KiBに対し今回119392 KiB。解なしだけで基底復元の速度やメモリを評価しない。

- [面積の比較記録](../benchmarks/results/rectangle_area_official_comparison.json)
- [連立方程式の比較記録](../benchmarks/results/f2_linear_equations_official_comparison.json)
- [解と基底の復元を含む比較記録](../benchmarks/results/f2_solution_recovery_official_comparison.json)
- [空間交差の比較記録](../benchmarks/results/f2_intersection_official_comparison.json)

## 単体検査

- 関連12テストが通過。
- 3記事のPython使用例4個も実行して通過した。
- 通常のquick検査169テストが通過。提出用コード・API・catalogの同期検査、説明監査（指摘0件）、再帰監査も通過した。
- quick性能回帰検査も通過。今回の公式ケース比較とは別の、通常の保守用検査。
- 小さい連立方程式の全解と照合し、返す基底の独立性・零空間・特解を確認する。
- 大きい長方形行列、階数0・1・7・8・9、128前後の切替境界、右辺整数/list、空の行・列を検査する。
- 空間交差は小さい値の全列挙、入力の非破壊性、10000ビットの値、一括構築と逐次追加の一致を検査する。
- 面積は単位マスの集合との照合、重複・辺の接触・負の座標・巨大整数・非2冪サイズ・横長/縦長の配置を検査する。
- XorBasis・面積の既存テストを、それぞれのmodule専用ファイルへ移した。

## 再実行

```sh
pypy3 library_codex/tools/check_library_checker.py test area_of_union_of_rectangles system_of_linear_equations_mod_2 intersection_of_f2_vector_spaces inverse_matrix_mod_2 matrix_det_mod_2 matrix_product_mod_2 matrix_rank_mod_2 --official /home/harurun/.cache/harurun-library-checker/problems --reuse-tests /home/harurun/.cache/online-judge-tools/library-checker-problems
pypy3 library_codex/benchmarks/official_benchmark.py area_of_union_of_rectangles system_of_linear_equations_mod_2 intersection_of_f2_vector_spaces inverse_matrix_mod_2 matrix_det_mod_2 matrix_product_mod_2 matrix_rank_mod_2 --official /home/harurun/.cache/harurun-library-checker/problems --repeat 5 --slowest 3
pypy3 library_codex/tools/prepare_checkpoint.py --profile quick
```

比較対象を再取得するには、各problemについて`benchmarks/library_checker.py fetch`を使う。保存したsnapshot内のsourceとhashを確認した後、次の形で比較する。snapshotの取得時点が変われば、対象となる提出も変わり得る。

```sh
pypy3 library_codex/benchmarks/official_comparison.py --snapshot ../lc-matching-reference/area_of_union_of_rectangles-pypy3.json --reviewed 394104 --problem /home/harurun/.cache/harurun-library-checker/problems/data_structure/area_of_union_of_rectangles --cases max_random_00 edge_bound_00 --variant previous=library_codex/benchmarks/baselines/area_of_union_of_rectangles_before.py --variant library=verify/library_checker/solutions/area_of_union_of_rectangles.py --repeat 5 --timeout 90 --output library_codex/benchmarks/results/rectangle_area_official_comparison.json
pypy3 library_codex/benchmarks/official_comparison.py --snapshot ../lc-matching-reference/system_of_linear_equations_mod_2-pypy3.json --reviewed 389265 --problem /home/harurun/.cache/harurun-library-checker/problems/linear_algebra/system_of_linear_equations_mod_2 --cases max_lowrank_00 max_lowrank_04 --variant previous=library_codex/benchmarks/baselines/system_of_linear_equations_mod_2_before.py --variant library=verify/library_checker/solutions/system_of_linear_equations_mod_2.py --repeat 5 --timeout 90 --output library_codex/benchmarks/results/f2_solution_recovery_official_comparison.json
```

全suiteのfull検査、オンライン提出、公開サイトの再デプロイはこの作業には含めない。
