import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from registry import load_banks, populated_banks  # noqa: E402
from utils import make_logger  # noqa: E402

SCRIPT_DIR = Path(__file__).resolve().parent
SUBS_PATH = SCRIPT_DIR / "subscriptions.json"

log = make_logger("pre-merge-commit")


def main():
    cwd = os.getcwd()
    try:
        banks = load_banks(SUBS_PATH)
    except Exception as e:
        log(f"failed to load subscriptions: {e}")
        print(f"{SCRIPT_TAG} failed to load subscriptions: {e}", file=sys.stderr)
        return 0

    nonempty = populated_banks(banks, cwd)
    if not nonempty:
        log("clean — no ungraduated banks")
        return 0

    names = [b.get("name", str(p)) for b, p in nonempty]
    msg = f"blocked merge — ungraduated: {', '.join(names)}"
    log(msg)
    print("Merge blocked: ungraduated small-banks detected.", file=sys.stderr)
    print(f"  Run /mem-bank-big-bank to graduate: {', '.join(names)}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
