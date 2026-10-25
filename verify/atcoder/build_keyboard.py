import argparse
import ast
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "library_codex/tools"))

from build_codon import atomic_write
from build_library_catalog import build_standalone_code


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    source, _ = build_standalone_code(Path(__file__).with_name("abc434_g.py"), ROOT / "library_codex")
    source = ast.unparse(ast.parse(source)) + "\n"
    path = Path(__file__).with_name("abc434_g_standalone.py")
    if path.is_file():
        try:
            saved = ast.parse(path.read_text(encoding="utf-8"))
            if ast.dump(saved) == ast.dump(ast.parse(source)):
                return
        except SyntaxError:
            pass
    if args.check:
        raise SystemExit("Keyboard standalone is stale")
    else:
        atomic_write(path, source)


if __name__ == "__main__":
    main()
