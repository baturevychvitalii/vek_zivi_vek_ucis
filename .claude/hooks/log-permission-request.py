import json, os, sys
from datetime import datetime

inp = json.loads(sys.stdin.read())
tool_name = inp.get("tool_name", "")
if not tool_name:
    sys.exit(0)

tool_input = inp.get("tool_input", {})

if tool_name == "Bash":
    detail = tool_input.get("command", "")
elif tool_name in ("Write", "Edit", "Read"):
    detail = tool_input.get("file_path", "")
else:
    detail = ""

hooks_dir = os.path.dirname(os.path.abspath(__file__))
log_path = os.path.join(hooks_dir, "hooks.log")

entry = f"{tool_name}: {detail}" if detail else tool_name

with open(log_path, "a") as log:
    log.write(f"{datetime.now().isoformat()}\t[permission-request]\t{entry}\n")
