import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from registry import load_banks  # noqa: E402
from utils import make_logger  # noqa: E402

SCRIPT_DIR = Path(__file__).resolve().parent
SUBS_PATH = SCRIPT_DIR / "subscriptions.json"

log = make_logger("pre-merge-commit")


def git_show(ref, path):
    result = subprocess.run(
        ["git", "show", f"{ref}:{path}"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        return None
    return result.stdout


def main():
    try:
        banks = load_banks(SUBS_PATH)
    except Exception as e:
        log(f"failed to load subscriptions: {e}")
        print(f"pre-merge-commit: failed to load subscriptions: {e}", file=sys.stderr)
        return 0

    blocked = []
    for bank in banks:
        small_bank = Path(bank["bank"]) / "small-bank.md"
        content = git_show("MERGE_HEAD", str(small_bank))
        if content is not None and content.strip():
            blocked.append(bank.get("name", str(small_bank)))

    if not blocked:
        log("clean — no ungraduated banks on MERGE_HEAD")
        return 0

    names = ", ".join(blocked)
    log(f"blocked merge — ungraduated on MERGE_HEAD: {names}")
    print("Merge blocked: ungraduated small-banks detected on the branch being merged.", file=sys.stderr)
    print(f"  Run /mem-bank-big-bank to graduate: {names}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
