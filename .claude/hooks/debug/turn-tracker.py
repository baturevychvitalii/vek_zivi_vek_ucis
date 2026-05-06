import json, os, sys
from datetime import datetime

inp = json.loads(sys.stdin.read())
prompt = inp.get("prompt") or inp.get("user_prompt") or inp.get("message") or ""
if not prompt:
    sys.exit(0)

hooks_dir = os.path.dirname(os.path.abspath(__file__))
log_path = os.path.join(hooks_dir, "hooks.log")

words = prompt.split()[:5]
summary = " ".join(words)
if len(prompt.split()) > 5:
    summary += "..."

with open(log_path, "a") as log:
    log.write(f"{datetime.now().isoformat()}\tREQUEST\t{summary}\n")
