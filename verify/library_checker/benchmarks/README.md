# PyPy公式ケースのベンチマーク

公式全件検証後、各問題で時間のかかったケースを再測定した記録。時間は起動・JIT・入出力込みの中央値、メモリは測定中の最大RSS。オンライン提出は行わない。

全公式ケースの判定・単発時間は `../results/`、各回の時間・RSS・入力とソースのhashはリンク先のJSONを参照。環境が違う記録間の速度は直接比較しない。

| 問題 | 測定ケース / 公式全件 | 反復数 | 最大中央値（秒） | 最大RSS（MiB） | ソース同期 |
| --- | ---: | ---: | ---: | ---: | --- |
| [enumerate_quotients](enumerate_quotients.json) | 3 / 26 | 5 | 0.296 | 132.4 | 一致 |
| [enumerate_triangles](enumerate_triangles.json) | 3 / 17 | 5 | 0.246 | 88.1 | 一致 |
| [gcd_convolution](gcd_convolution.json) | 3 / 29 | 5 | 0.560 | 263.5 | 一致 |
| [inverse_matrix](inverse_matrix.json) | 3 / 26 | 5 | 1.195 | 82.2 | 一致 |
| [inverse_matrix_mod_2](inverse_matrix_mod_2.json) | 3 / 37 | 5 | 2.399 | 153.9 | 一致 |
| [lcm_convolution](lcm_convolution.json) | 3 / 29 | 5 | 0.590 | 263.6 | 一致 |
| [longest_increasing_subsequence](longest_increasing_subsequence.json) | 3 / 19 | 5 | 0.256 | 118.3 | 一致 |
| [lyndon_factorization](lyndon_factorization.json) | 3 / 23 | 5 | 0.175 | 107.6 | 一致 |
| [matrix_det](matrix_det.json) | 3 / 25 | 5 | 0.376 | 64.4 | 一致 |
| [matrix_det_mod_2](matrix_det_mod_2.json) | 3 / 36 | 5 | 0.481 | 66.2 | 一致 |
| [matrix_product_mod_2](matrix_product_mod_2.json) | 3 / 26 | 5 | 1.913 | 147.2 | 一致 |
| [matrix_rank](matrix_rank.json) | 3 / 36 | 5 | 0.404 | 64.4 | 一致 |
| [matrix_rank_mod_2](matrix_rank_mod_2.json) | 3 / 35 | 5 | 1.606 | 315.5 | 一致 |
| [montmort_number_mod](montmort_number_mod.json) | 3 / 10 | 5 | 0.149 | 90.1 | 一致 |
| [system_of_linear_equations](system_of_linear_equations.json) | 3 / 27 | 5 | 0.525 | 66.6 | 一致 |
