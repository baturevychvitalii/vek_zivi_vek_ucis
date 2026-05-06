import json, os, sys
from datetime import datetime

inp = json.loads(sys.stdin.read())
exit_reason = inp.get("exit_reason", "unknown")

hooks_dir = os.path.dirname(os.path.abspath(__file__))
log_path = os.path.join(hooks_dir, "hooks.log")

with open(log_path, "a") as log:
    log.write(f"{datetime.now().isoformat()}\t[session-end]\t{exit_reason}\n")
