"""Create a human-authored article skeleton for one public module."""

import argparse
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def normalize_module_key(value):
    value = value.replace("\\", "/")
    if value.startswith("library_codex/"):
        value = value[len("library_codex/"):]
    if value.endswith(".py"):
        value = value[:-3]
    parts = value.split("/")
    if len(parts) != 2 or not all(parts):
        raise ValueError("module must be written as category/Module")
    return parts[0], parts[1]


def article_template(category, name):
    return f"""# {name}でできること

## 主な機能

TODO: どんな入力に対して、何を高速に求められるかを具体的に書く。

## 使い方

```python
from library_codex.{category}.{name} import ...
```

TODO: 最小の使用例と、返り値をどう読むかを書く。

## 注意点

TODO: 適用条件や似たmoduleとの違いがある場合だけ書く。
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("module", help="category/Module or its source path")
    args = parser.parse_args()
    category, name = normalize_module_key(args.module)
    source = ROOT / category / f"{name}.py"
    if not source.is_file():
        raise SystemExit(f"public module does not exist: {source}")
    output = ROOT / "docs" / "articles" / category / f"{name}.md"
    if output.exists():
        raise SystemExit(f"article already exists: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(article_template(category, name), encoding="utf-8")
    print(output.relative_to(ROOT.parent).as_posix())


if __name__ == "__main__":
    main()

