from library_codex.heuristic.Heuristics import LogTable, MultiArmedBandit, TopK


def test_log_table_bandit_and_top_k():
    table = LogTable(bits=10)
    assert all(value <= 0 for value in table.values)
    assert table(17) == table(17 + 1024)
    bandit = MultiArmedBandit(4, seed=91)
    for _ in range(1000):
        arm = bandit.play()
        bandit.reward(10 if arm == 2 else 0)
    assert bandit.best() == 2
    top = TopK(10, hash_function=lambda value: value % 17)
    for value in range(1000, -1, -1):
        top.insert(value)
    result = top.get()
    assert len(result) == 10
    assert result == sorted(result)
    assert len({value % 17 for value in result}) == 10
