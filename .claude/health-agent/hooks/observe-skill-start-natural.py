import json, os, sys
from datetime import datetime

IGNORED_SKILLS = []

hooks_dir = os.path.dirname(os.path.abspath(__file__))
subsystem_dir = os.path.dirname(hooks_dir)
log_path = os.path.join(subsystem_dir, "hooks.log")


def log(msg):
    with open(log_path, "a") as f:
        f.write(f"{datetime.now().isoformat()}\t[observe-skill-start-natural]\t{msg}\n")


inp = json.loads(sys.stdin.read())

tool_name = inp.get("tool_name", "")
if tool_name != "Skill":
    log(f"skip: tool_name={tool_name} is not Skill")
    sys.exit(0)

skill = inp.get("tool_input", {}).get("skill", "")
if not skill:
    log("skip: no skill name in tool_input")
    sys.exit(0)
if skill in IGNORED_SKILLS:
    log(f"skip: skill={skill} is in IGNORED_SKILLS")
    sys.exit(0)

transcript_path = inp.get("transcript_path", "")
summary_path = os.path.join(subsystem_dir, "run-summary.json")

log(f"recorded skill={skill} transcript={transcript_path or 'none'}")

with open(summary_path, "w") as f:
    json.dump({
        "skill": skill,
        "started_at": datetime.utcnow().isoformat() + "Z",
        "transcript_path": transcript_path,
    }, f, indent=2)
