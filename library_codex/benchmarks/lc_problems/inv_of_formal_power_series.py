from library_codex.benchmarks.lc_problems._series import fps_case


MODULE = "fps998/FPS.py"
FAMILIES = ("dense", "sparse")


def make_case(n, family, seed):
    return fps_case(n, family, seed, "inv")


def solve():
    n = int(sys.stdin.buffer.readline())
    a = list(map(int, sys.stdin.buffer.readline().split()))
    print(" ".join(map(str, fps_inv(a, n))))
