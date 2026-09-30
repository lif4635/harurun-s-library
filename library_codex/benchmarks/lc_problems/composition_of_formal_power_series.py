from library_codex.benchmarks.lc_problems._composition import composition_case, solve, solve_trimmed


MODULE = "fps998/Composition.py"
MAX_SIZE = 8000
FAMILIES = ("dense", "sparse_inner", "identity")
VARIANTS = {"trimmed": (MODULE, "solve_trimmed")}


def make_case(n, family, seed):
    return composition_case(n, family, seed)
