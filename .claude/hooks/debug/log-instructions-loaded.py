import json, os, sys
from datetime import datetime

inp = json.loads(sys.stdin.read())
file_path = inp.get("file_path", "")
if not file_path:
    sys.exit(0)

load_reason = inp.get("load_reason", "unknown")
cwd = inp.get("cwd", "")

if cwd and file_path.startswith(cwd):
    rel = file_path[len(cwd):].lstrip("/")
else:
    rel = file_path

hooks_dir = os.path.dirname(os.path.abspath(__file__))
log_path = os.path.join(hooks_dir, "hooks.log")

with open(log_path, "a") as log:
    log.write(f"{datetime.now().isoformat()}\t[instructions-loaded]\t{load_reason}: {rel}\n")
