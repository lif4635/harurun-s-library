import random
from pathlib import Path
import subprocess
import sys

import pytest

from library_codex.number_theory.DecimalAddition import add_decimal
from library_codex.tools.build_library_catalog import build_standalone_code


def test_decimal_addition_against_integers():
    rng = random.Random(613801)
    for _ in range(4000):
        a = rng.randrange(-10**300, 10**300)
        b = rng.randrange(-10**rng.randrange(1, 301), 10**rng.randrange(1, 301))
        assert add_decimal(str(a), str(b)) == str(a + b)
        assert add_decimal(str(b), str(a)) == str(a + b)


def test_decimal_addition_long_carries_and_cancellation():
    n = 2000000
    assert add_decimal("9" * n, "1") == "1" + "0" * n
    assert add_decimal("1" + "0" * n, "-1") == "9" * n
    assert add_decimal("-" + "9" * n, "9" * n) == "0"
    assert add_decimal("-1", "-" + "9" * n) == "-1" + "0" * n


def test_decimal_addition_normalization_and_invalid_strings():
    assert add_decimal("-000", "+000") == "0"
    assert add_decimal("+00012", "-0013") == "-1"
    assert add_decimal("-0", "-00000") == "0"
    for text in ("", "+", "-", " 1", "1 ", "1_0", "1.0", "１２", "--1"):
        with pytest.raises(ValueError):
            add_decimal(text, "1")


def test_decimal_addition_small_input_and_chunk_boundaries():
    values = [0, 1, -1]
    for digits in (8, 9, 10, 17, 18, 19, 26, 27, 28):
        for delta in (-1, 0, 1):
            values.extend((10**digits + delta, -10**digits + delta))
    for a in values:
        for b in values:
            assert add_decimal(str(a), str(b)) == str(a + b)


def test_decimal_addition_standalone(tmp_path):
    root = Path(__file__).resolve().parents[2]
    source, dependencies = build_standalone_code(root / "number_theory/DecimalAddition.py", root)
    assert dependencies == []
    script = tmp_path / "main.py"
    script.write_text(source + '\nassert add_decimal("9" * 5000, "1") == "1" + "0" * 5000\n', encoding="utf-8")
    subprocess.run([sys.executable, "-I", str(script)], cwd=tmp_path, check=True, timeout=30)
