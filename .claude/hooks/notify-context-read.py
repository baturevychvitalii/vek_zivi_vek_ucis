import json, os, sys
from datetime import datetime

inp = json.loads(sys.stdin.read())
path = inp.get("tool_input", {}).get("file_path", "")

hooks_dir = os.path.dirname(os.path.abspath(__file__))
log_path = os.path.join(hooks_dir, "hooks.log")

if path.endswith("/context.md") or path == "context.md":
    project_root = os.path.dirname(hooks_dir)
    try:
        rel = os.path.relpath(path, project_root)
    except ValueError:
        rel = path

    with open(log_path, "a") as _log:
        _log.write(f"{datetime.now().isoformat()}\t[notify-context-read]\t{rel}\n")
