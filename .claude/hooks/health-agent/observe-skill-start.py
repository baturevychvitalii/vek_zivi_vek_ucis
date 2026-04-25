import json, os, sys
from datetime import datetime

IGNORED_SKILLS = []

inp = json.loads(sys.stdin.read())

prompt = inp.get("prompt", "").strip()
if not prompt.startswith("/"):
    sys.exit(0)

# Extract command name: "/pipe:anki-add-cards some args" → "pipe:anki-add-cards"
command_name = prompt.lstrip("/").split()[0]

if command_name in IGNORED_SKILLS:
    sys.exit(0)

transcript_path = inp.get("transcript_path", "")

hooks_dir = os.path.dirname(os.path.abspath(__file__))
summary_path = os.path.join(hooks_dir, "run-summary.json")

with open(summary_path, "w") as f:
    json.dump({
        "skill": command_name,
        "started_at": datetime.utcnow().isoformat() + "Z",
        "transcript_path": transcript_path,
    }, f, indent=2)
