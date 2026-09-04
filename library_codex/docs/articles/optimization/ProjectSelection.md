# 0/1コストを最小カットで解く Project Selection

## 主な機能

$N$ 個の変数 $x_i\in\{0,1\}$ に対し、一変数のコスト、二変数の組合せごとのコスト、複数変数がすべて0またはすべて1のときの利益を足し、合計コストが最小になる割当を求めます。利益は負のコストとして登録できます。

項は追加時には辺へ変換せず、`build()`で同じ変数対の項を合算してから`MaxFlowGraph`へ変換します。各コストには負数を使え、`math.inf`を指定した割当は禁止条件として扱えます。

## 使い方

```python
from math import inf

from library_codex.optimization.ProjectSelection import ProjectSelection

solver = ProjectSelection(3)
solver.add_unary_cost(0, 5, -2)
solver.add_cost_01(0, 1, 8)
solver.add_pair_cost(1, 2, [[0, 0], [inf, -3]])

cost, assignment = solver.min_cost()
```

- `cost`: 登録した全項の合計の最小値。
- `assignment[i]`: 変数 $x_i$ に割り当てた0または1。
- この例の`math.inf`: $(x_1,x_2)=(1,0)$ を禁止する。

## build

最小カットの辺を追加したり、`MaxFlowGraph`を直接調べたい場合は`min_cost()`の代わりに`build()`を使います。

```python
graph, offset = solver.build()
value = offset + graph.flow(solver.source, solver.sink)
reachable = graph.min_cut(solver.source)
assignment = [0 if reachable[i] else 1 for i in range(3)]
```

- `graph`: 非負の有限容量だけを持つ`MaxFlowGraph`。
- `offset`: 最小カット値へ足す定数。
- source側の変数は0、sink側の変数は1になる。
- `build()`または`min_cost()`の後には項を追加できない。

## 二変数コストの条件

`add_pair_cost(i, j, costs)`では`costs[a][b]`が$(x_i,x_j)=(a,b)$のときのコストです。同じ変数対へ追加した表をすべて合算した結果が、次を満たす必要があります。

$$
C_{00}+C_{11}\le C_{01}+C_{10}
$$

各項が単独でこの条件を満たす必要はありません。負の`add_cost_01`を追加しても、後から同じ変数対へ足した項との合計が条件を満たせば`build()`できます。

## 注意点

- `math.inf`は一変数または二変数コストで、その状態を禁止するときに使う。
- `-math.inf`と`NaN`は使えない。
- 禁止条件が矛盾して実行可能な割当がない場合、`min_cost()`は`ValueError`を送出する。
- `add_profit_all_zero`と`add_profit_all_one`の利益は有限の非負値に限る。
- `MaxFlowGraph`へ負容量や無限容量が渡ることはない。
