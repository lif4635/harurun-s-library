"""Generate derived files, run the right checks, and optionally sync the site."""

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = ROOT.parent
TOOLS = ROOT / "tools"


def run_step(label, command, cwd=REPOSITORY):
    print(f"\n== {label} ==", flush=True)
    completed = subprocess.run(command, cwd=cwd)
    if completed.returncode:
        raise SystemExit(completed.returncode)


def check_command(profile, benchmarks=True):
    if profile == "changed":
        command = [sys.executable, str(TOOLS / "check_changed.py")]
        if benchmarks:
            command.append("--benchmarks")
        return command
    command = [sys.executable, str(TOOLS / "check_library.py")]
    if profile == "full":
        command.extend(("--profile", "full"))
    return command


def site_sync_command(site_root):
    site_root = site_root.resolve()
    script = site_root / "scripts" / "sync_library_data.py"
    hosting = site_root / ".openai" / "hosting.json"
    if not script.is_file() or not hosting.is_file():
        raise ValueError(
            f"site directory is missing sync_library_data.py or hosting.json: {site_root}"
        )
    return [
        sys.executable,
        str(script),
        str(ROOT),
        str(site_root / "app" / "library-data.json"),
        "--code-output",
        str(site_root / "public"),
        "--incremental",
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--profile",
        choices=("changed", "quick", "full"),
        default="changed",
        help="changed is for iteration, quick for checkpoints, full for releases",
    )
    parser.add_argument(
        "--no-benchmarks",
        action="store_true",
        help="skip quick performance checks with the changed profile",
    )
    parser.add_argument(
        "--site",
        type=Path,
        help="site repository to update after library checks pass",
    )
    args = parser.parse_args()

    run_step(
        "API reference generation",
        [sys.executable, str(TOOLS / "build_api_reference.py")],
    )
    run_step(
        "library catalog generation",
        [sys.executable, str(TOOLS / "build_library_catalog.py")],
    )
    run_step(
        f"{args.profile} library checks",
        check_command(args.profile, not args.no_benchmarks),
    )
    if args.site is not None:
        try:
            command = site_sync_command(args.site)
        except ValueError as error:
            parser.error(str(error))
        run_step("site catalog synchronization", command, args.site.resolve())

    print("\nCheckpoint is ready to review and commit.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
