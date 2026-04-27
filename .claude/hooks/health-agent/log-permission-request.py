import json, os, sys
from datetime import datetime

inp = json.loads(sys.stdin.read())
tool_name = inp.get("tool_name", "")
if not tool_name:
    sys.exit(0)

tool_input = inp.get("tool_input", {})
transcript_path = inp.get("transcript_path", "")

if tool_name == "Bash":
    detail = tool_input.get("command", "")
elif tool_name in ("Write", "Edit", "Read"):
    detail = tool_input.get("file_path", "")
else:
    detail = ""

hooks_dir = os.path.dirname(os.path.abspath(__file__))
events_path = os.path.join(hooks_dir, "permission-events.jsonl")
log_path = os.path.join(hooks_dir, "hooks.log")

with open(events_path, "a") as f:
    f.write(json.dumps({
        "timestamp": datetime.now().isoformat(),
        "tool_name": tool_name,
        "detail": detail,
        "transcript_path": transcript_path,
    }) + "\n")

with open(log_path, "a") as f:
    f.write(f"{datetime.now().isoformat()}\t[log-permission-request]\ttool={tool_name} detail={detail[:120]!r}\n")
