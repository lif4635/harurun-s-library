# 元の `library` から取り込んだもの

元の `library` は比較用としてそのまま残し、今後使う実装は `library_codex` に集約します。単純な全コピーではなく、`library_codex` にない用途だけを選び、未定義変数・境界条件・再帰依存を直して移植しました。

## 今回取り込んだ機能

| 元の着想 | `library_codex` の配置 | 主な改善 |
| --- | --- | --- |
| 外積・向き判定 | `geometry/Orientation.py` | 返り値の意味を固定し、整数演算だけで判定 |
| 線分交差判定 | `geometry/SegmentIntersection.py` | 端点接触を含めるか選択可能 |
| 凸包 | `geometry/ConvexHull.py` | 未定義変数を除去し、重複点・一直線・端点重複を処理 |
| 偏角sort | `geometry/ArgumentSort.py` | 浮動小数点数を使わず、同じ向きの順序も決定的にした |
| grid BFS | `shortest_path/GridBFS.py` | 方向定数への暗黙依存をなくし、距離表と2点間距離を分離 |
| 整数n乗根 | `algorithm/IntegerUtilities.py` | 非負整数に対するfloor値を二分探索で返す |
| Gray codeの端点指定path | `combinatorics/GrayCode.py` | 全maskを1回ずつ通るgeneratorとして追加 |
| 二項係数prefix和の移動 | `combinatorics/BinomialQueries.py` | `(n, m)` を前後に動かせる `BinomialPrefix` として整理 |
| 0/1 treeの転倒数最小化 | `tree/ZeroOneTree.py` | 未定義変数を除去し、反復heap処理と入力検証を追加 |

## 既により強い実装があるもの

元のSegment Tree、Lazy Segment Tree、Union-Find、Fenwick Tree、Sparse Table、畳み込み、FPS、素因数分解、文字列、graph、tree、探索・sort系の大部分は、同じ用途または上位の用途を `library_codex` が既に持っています。これらは重複APIを増やさず、既存の高速・非再帰実装を正本にします。

## 取り込まなかったもの

- 巨大な乱数前計算を持つ `ModFast` は、memory消費と再現性に対して用途が狭いため不採用です。
- 独自deque・hash set・hash dict・quick sortは、Python標準実装より安全性または速度で優位にならないため不採用です。
- 元の `SqrtTree.py` は実質的に平方分割で、既存のSegment Tree・Disjoint Sparse Tableより用途が狭いため不採用です。
- global変数に依存するBell数・区間基底などはそのまま移植せず、必要になった時点で独立APIとして再設計します。

`library` は削除していません。差分確認と、まだ拾えていない着想を調べるための参照元として保持します。
