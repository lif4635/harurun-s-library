import importlib
import inspect
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
PROBLEMS = tuple(sorted(path.stem for path in Path(__file__).parent.glob("*.py") if not path.stem.startswith("_")))


def problem_module(name):
    if name not in PROBLEMS:
        raise ValueError("unknown problem: " + name)
    sys.path.insert(0, str(ROOT.parent))
    return importlib.import_module("library_codex.benchmarks.lc_problems." + name)


def standalone(name, variant=None):
    from library_codex.tools.build_library_catalog import build_standalone_code

    module = problem_module(name)
    path, function = (module.MODULE, module.solve) if variant is None else (
        module.VARIANTS[variant][0], getattr(module, module.VARIANTS[variant][1]))
    source, dependencies = build_standalone_code(ROOT / path, ROOT)
    driver = inspect.getsource(function).replace("def " + function.__name__ + "(", "def solve(", 1)
    return (source + "\nimport sys\n" + driver + "\nsolve()\n").encode()
