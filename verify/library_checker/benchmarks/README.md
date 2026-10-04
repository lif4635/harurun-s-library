# PyPy公式ケースのベンチマーク

公式全件検証後、各問題で時間のかかったケースを再測定した記録。時間は起動・JIT・入出力込みの中央値、メモリは測定中の最大RSS。オンライン提出は行わない。

全公式ケースの判定・単発時間は `../results/`、各回の時間・RSS・入力とソースのhashはリンク先のJSONを参照。環境が違う記録間の速度は直接比較しない。

| 問題 | 測定ケース / 公式全件 | 反復数 | 最大中央値（秒） | 最大RSS（MiB） | ソース同期 |
| --- | ---: | ---: | ---: | ---: | --- |
| [bell_number](bell_number.json) | 3 / 11 | 5 | 1.169 | 149.8 | 一致 |
| [bernoulli_number](bernoulli_number.json) | 3 / 11 | 5 | 0.650 | 108.1 | 一致 |
| [enumerate_quotients](enumerate_quotients.json) | 3 / 26 | 5 | 0.296 | 132.4 | 一致 |
| [enumerate_triangles](enumerate_triangles.json) | 3 / 17 | 5 | 0.246 | 88.1 | 一致 |
| [exp_of_formal_power_series_sparse](exp_of_formal_power_series_sparse.json) | 3 / 25 | 5 | 0.245 | 122.7 | 一致 |
| [exp_of_set_power_series](exp_of_set_power_series.json) | 3 / 13 | 5 | 2.261 | 345.6 | 一致 |
| [gcd_convolution](gcd_convolution.json) | 3 / 29 | 5 | 0.560 | 263.5 | 一致 |
| [inv_of_formal_power_series_2d](inv_of_formal_power_series_2d.json) | 3 / 28 | 5 | 1.476 | 139.9 | 一致 |
| [inv_of_formal_power_series_sparse](inv_of_formal_power_series_sparse.json) | 3 / 24 | 5 | 0.195 | 105.9 | 一致 |
| [inverse_matrix](inverse_matrix.json) | 3 / 26 | 5 | 1.195 | 82.2 | 一致 |
| [inverse_matrix_mod_2](inverse_matrix_mod_2.json) | 3 / 37 | 5 | 2.399 | 153.9 | 一致 |
| [lcm_convolution](lcm_convolution.json) | 3 / 29 | 5 | 0.590 | 263.6 | 一致 |
| [log_of_formal_power_series_sparse](log_of_formal_power_series_sparse.json) | 3 / 24 | 5 | 0.301 | 140.1 | 一致 |
| [log_of_set_power_series](log_of_set_power_series.json) | 3 / 12 | 5 | 5.285 | 379.7 | 一致 |
| [longest_increasing_subsequence](longest_increasing_subsequence.json) | 3 / 19 | 5 | 0.256 | 118.3 | 一致 |
| [lyndon_factorization](lyndon_factorization.json) | 3 / 23 | 5 | 0.175 | 107.6 | 一致 |
| [matrix_det](matrix_det.json) | 3 / 25 | 5 | 0.376 | 64.4 | 一致 |
| [matrix_det_mod_2](matrix_det_mod_2.json) | 3 / 36 | 5 | 0.481 | 66.2 | 一致 |
| [matrix_product_mod_2](matrix_product_mod_2.json) | 3 / 26 | 5 | 1.913 | 147.2 | 一致 |
| [matrix_rank](matrix_rank.json) | 3 / 36 | 5 | 0.404 | 64.4 | 一致 |
| [matrix_rank_mod_2](matrix_rank_mod_2.json) | 3 / 35 | 5 | 1.606 | 315.5 | 一致 |
| [montmort_number_mod](montmort_number_mod.json) | 3 / 10 | 5 | 0.149 | 90.1 | 一致 |
| [partition_function](partition_function.json) | 3 / 11 | 5 | 0.677 | 98.6 | 一致 |
| [polynomial_composite_set_power_series](polynomial_composite_set_power_series.json) | 3 / 18 | 5 | 5.367 | 359.6 | 一致 |
| [pow_of_formal_power_series_sparse](pow_of_formal_power_series_sparse.json) | 3 / 35 | 5 | 0.309 | 138.2 | 一致 |
| [power_projection_of_set_power_series](power_projection_of_set_power_series.json) | 3 / 30 | 5 | 4.099 | 441.4 | 一致 |
| [sqrt_of_formal_power_series_sparse](sqrt_of_formal_power_series_sparse.json) | 3 / 45 | 5 | 0.277 | 142.3 | 一致 |
| [stirling_number_of_the_first_kind](stirling_number_of_the_first_kind.json) | 3 / 10 | 5 | 0.833 | 97.0 | 一致 |
| [stirling_number_of_the_first_kind_fixed_k](stirling_number_of_the_first_kind_fixed_k.json) | 3 / 14 | 5 | 1.960 | 185.2 | 一致 |
| [stirling_number_of_the_second_kind](stirling_number_of_the_second_kind.json) | 3 / 10 | 5 | 0.608 | 109.4 | 一致 |
| [stirling_number_of_the_second_kind_fixed_k](stirling_number_of_the_second_kind_fixed_k.json) | 3 / 14 | 5 | 1.992 | 187.8 | 一致 |
| [subset_convolution](subset_convolution.json) | 3 / 11 | 5 | 2.647 | 575.1 | 一致 |
| [system_of_linear_equations](system_of_linear_equations.json) | 3 / 27 | 5 | 0.525 | 66.6 | 一致 |
