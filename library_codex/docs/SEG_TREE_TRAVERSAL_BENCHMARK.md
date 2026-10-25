# 子孫参照マージのセグメント木：Keyboardでの比較

2026-10-25測定。共通関数は`segment_tree/SegTreeTraversal.py`、利用例は`verify/atcoder/abc434_g.py`。通常の`SegTree`は変更していない。

## 比較条件

- PyPy 7.3.16 / Python 3.10.14、WSL2 Linux、CPU 2へ固定して逐次実行。
- 各回を新しいprocessで実行し、事前warmupなし。JIT時間を含む。
- 小規模比較は20万文字・3万操作、更新と取得を交互に実施。各候補3回の中央値。
- `mixed`は数字とBをほぼ同数、`digits`は数字のみで構築後にBを含む更新、`cancellation`は63桁と32個のBの繰り返しから開始する。
- 時間は構築と全操作の合計。入力生成・Pythonの起動・標準入出力は除く。RSSは入力生成を含むprocess全体の最大値。
- 同じseed・入力hash・結果checksumを照合。小さいケースの正しさは別途、単純な末尾削除と比較する。
- OS全体の負荷は隔離していない。細かい差はJITと実行時の揺れも含む。

## 区間走査と保存形式

| 方式 | mixed | digits | cancellation |
| --- | ---: | ---: | ---: |
| 共通関数・右端から直接切り出す方式 | 0.160秒 | 0.110秒 | 0.188秒 |
| 同じ走査をKeyboard.prodへ直接記述 | 0.176秒 | 0.104秒 | 0.214秒 |
| 左側ノードを一時listへ積む方式 | 0.209秒 | 0.154秒 | 0.264秒 |
| 直接切り出す方式・保存配列をlist化 | 0.191秒 | 0.126秒 | 0.258秒 |

右端から最大の整列済み区間を切り出す方式を採用した。`fold`自体はO(1)追加メモリで、callbackへ渡すのは実在するノードの整数添字だけ。直接記述との差はこの測定では小さく、共通化による一貫した大幅な悪化は見られなかった。あらゆるcallbackで同じ速度になる保証ではない。

Keyboardでは`array("I")`に個数・長さ・値を別々に保存する。ノードごとのclassやtupleを避け、内部ノードには左から残った数値をキャッシュする。逆数の表と再帰呼出しを使わず、必要な先頭桁だけを一方の子へ降りて求める。

[比較の生データ](../benchmarks/results/seg_tree_traversal_comparison.json)には全36試行、RSS、入力・source hash、環境情報を保存した。初期の探索記録は`seg_tree_traversal.json`、採用直後の確認は`seg_tree_traversal_selected.json`に残している。初期記録の`shared`は一時list方式であり、採用後の`shared`とは異なる。

## 上限サイズと提出コード

800万文字・20万操作で共通版と直接記述版を1回ずつ比較した。構築と操作の合計は、繰り返し相殺入力で2.084秒 / 1.986秒、数字中心入力で1.066秒 / 1.086秒。これは反復平均ではなく1回の測定。[生データ](../benchmarks/results/seg_tree_traversal_large.json)

さらに、依存を展開した`abc434_g_standalone.py`を隔離processで3回実行した。

- 入力は800万文字・20万操作の独自の繰り返し相殺ケース。
- 起動・JIT・標準入力の解析・標準出力をすべて含む。
- 2.451 / 2.339 / 2.465秒、中央値2.451秒。
- 最大RSSは343696 KiB、約335.6 MiB。
- 出力全文をimport版と照合した。大規模ケースの比較相手は同じアルゴリズムであり、独立した正当性検査は小さい入力の単純解比較が担当する。

[提出コードの測定記録](../benchmarks/results/keyboard_standalone.json)

公式ケース全件・オンライン提出は未実施。この測定だけからAtCoderでのACや3秒以内を保証しない。

## 再実行

リポジトリ直下で実行する。ベンチマークはLinux/WSL向け。WSL内の別のcheckoutを更新する必要はない。

```sh
pypy3 verify/atcoder/build_keyboard.py
pypy3 -m pytest -q library_codex/verify/segment_tree/test_seg_tree_traversal.py
taskset -c 2 pypy3 -m library_codex.benchmarks.seg_tree_traversal --output library_codex/benchmarks/results/seg_tree_traversal_comparison.json
taskset -c 2 pypy3 -m verify.atcoder.benchmark_keyboard --output library_codex/benchmarks/results/keyboard_standalone.json
```

`build_keyboard.py --check`で保存済み提出コードとsourceの同期を検査できる。この検査は専用pytestにも含まれる。
