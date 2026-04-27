import json, os, sys
from datetime import datetime

IGNORED_SKILLS = []

hooks_dir = os.path.dirname(os.path.abspath(__file__))
log_path = os.path.join(hooks_dir, "hooks.log")


def log(msg):
    with open(log_path, "a") as f:
        f.write(f"{datetime.now().isoformat()}\t[observe-skill-start]\t{msg}\n")


inp = json.loads(sys.stdin.read())

prompt = inp.get("prompt", "").strip()
if not prompt.startswith("/"):
    log(f"skip: prompt is not a slash command")
    sys.exit(0)

# Extract command name: "/pipe:anki-add-cards some args" → "pipe:anki-add-cards"
command_name = prompt.lstrip("/").split()[0]

if command_name in IGNORED_SKILLS:
    log(f"skip: skill={command_name} is in IGNORED_SKILLS")
    sys.exit(0)

transcript_path = inp.get("transcript_path", "")
summary_path = os.path.join(hooks_dir, "run-summary.json")

with open(summary_path, "w") as f:
    json.dump({
        "skill": command_name,
        "started_at": datetime.utcnow().isoformat() + "Z",
        "transcript_path": transcript_path,
    }, f, indent=2)

log(f"recorded skill={command_name}")
