import json, os, sys, glob
from datetime import datetime

sys.stdin.read()  # consume stdin (Stop hook provides it; fields not documented)

hooks_dir = os.path.dirname(os.path.abspath(__file__))
log_path = os.path.join(hooks_dir, "hooks.log")
summary_path = os.path.join(hooks_dir, "run-summary.json")


def log(msg):
    with open(log_path, "a") as f:
        f.write(f"{datetime.now().isoformat()}\t[observe-session-health]\t{msg}\n")

if not os.path.exists(summary_path):
    log("skip: no run-summary.json found")
    sys.exit(0)

with open(summary_path) as f:
    summary = json.load(f)

skill = summary.get("skill", "")

# Fuzzy-match skill name against pipeline spec filenames.
# "anki-add-cards" → looks for a spec whose stem is a suffix of the skill name.
project_root = os.path.dirname(hooks_dir)
specs = glob.glob(os.path.join(project_root, ".claude", "pipeline-specifications", "*.md"))
spec_path = ""
for spec in specs:
    stem = os.path.splitext(os.path.basename(spec))[0]
    if skill.endswith(stem):
        spec_path = os.path.relpath(spec, project_root)
        break

summary["completed_at"] = datetime.now().isoformat()
if spec_path:
    summary["pipeline_spec_path"] = spec_path

with open(summary_path, "w") as f:
    json.dump(summary, f, indent=2)

log(f"stamped completed_at for skill={skill}" + (f" spec={spec_path}" if spec_path else ""))
