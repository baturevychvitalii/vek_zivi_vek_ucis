import json
import shlex
import subprocess
import sys
from pathlib import Path

HOOK_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(HOOK_DIR.parent.parent / ".claude"))
from utils.log import make_logger  # noqa: E402

log = make_logger("gh-issue-label-gate", HOOK_DIR / "scm-integration.log")

BLOCKED = "Blocked: every GitHub issue needs at least one label (labeling strategy, system/README.md)."
CLOSING = "If the fit is ambiguous or no suitable label exists, ask the user — do not invent one."


def tokenize(command):
    try:
        return shlex.split(command)
    except ValueError:
        return command.split()


def is_unlabeled_issue_create(tokens):
    if not tokens or Path(tokens[0]).name != "gh":
        return False
    if not any(a == "issue" and b == "create" for a, b in zip(tokens, tokens[1:])):
        return False
    return not any(t in ("--label", "-l") or t.startswith("--label=") for t in tokens)


def repo_flag(tokens):
    for a, b in zip(tokens, tokens[1:] + [""]):
        if a in ("--repo", "-R"):
            return [a, b]
        if a.startswith("--repo="):
            return [a]
    return []


def existing_labels(tokens):
    cmd = ["gh", "label", "list", "--limit", "100", "--json", "name", "--jq", ".[].name"]
    cmd += repo_flag(tokens)
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if out.returncode == 0:
            return [line for line in out.stdout.splitlines() if line.strip()]
    except Exception as e:
        log(f"label discovery failed: {e}")
    return None


def guidance(labels):
    if labels:
        return f"{BLOCKED}\nExisting labels: {', '.join(labels)}\nRetry with --label <name> (repeatable). {CLOSING}"
    if labels == []:
        return f"{BLOCKED}\nThe repo has no labels yet — ask the user which label to create."
    return f"{BLOCKED}\nDiscover existing labels (gh label list), assess fit, retry with --label <name>. {CLOSING}"


def main():
    try:
        payload = json.load(sys.stdin)
        command = (payload.get("tool_input") or {}).get("command", "")
        tokens = tokenize(command)
        if not is_unlabeled_issue_create(tokens):
            return 0
    except Exception as e:
        log(f"fail-open: {e}")
        return 0
    labels = existing_labels(tokens)
    log(f"blocked unlabeled issue create (labels offered: {labels is not None}): {command[:200]}")
    print(guidance(labels), file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
