import json, os, sys
from datetime import datetime

IGNORED_SKILLS = []

inp = json.loads(sys.stdin.read())

tool_name = inp.get("tool_name", "")
if tool_name != "Skill":
    sys.exit(0)

skill = inp.get("tool_input", {}).get("skill", "")
if not skill or skill in IGNORED_SKILLS:
    sys.exit(0)

transcript_path = inp.get("transcript_path", "")

hooks_dir = os.path.dirname(os.path.abspath(__file__))
log_path = os.path.join(hooks_dir, "hooks.log")
summary_path = os.path.join(hooks_dir, "run-summary.json")

with open(log_path, "a") as log:
    log.write(f"{datetime.now().isoformat()}\t[observe-skill-start-natural]\tskill={skill} transcript={transcript_path or 'none'}\n")

with open(summary_path, "w") as f:
    json.dump({
        "skill": skill,
        "started_at": datetime.now().isoformat(),
        "transcript_path": transcript_path,
    }, f, indent=2)
