import json, os, sys
from datetime import datetime

inp = json.loads(sys.stdin.read())
path = inp.get("tool_input", {}).get("file_path", "")

hooks_dir = os.path.dirname(os.path.abspath(__file__))
log_path = os.path.join(hooks_dir, "hooks.log")

marker = "/.claude/meta/"

if marker in path:
    rel = path.split(marker)[-1]

    with open(log_path, "a") as _log:
        _log.write(f"{datetime.now().isoformat()} [notify-meta-read] {rel}\n")

