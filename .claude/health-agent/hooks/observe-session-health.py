import json, os, sys, glob
from datetime import datetime
from pathlib import Path

sys.stdin.read()  # consume stdin (Stop hook provides it; fields not documented)

hooks_dir = os.path.dirname(os.path.abspath(__file__))
subsystem_dir = os.path.dirname(hooks_dir)
claude_dir = os.path.dirname(subsystem_dir)
project_root = os.path.dirname(claude_dir)
log_path = os.path.join(subsystem_dir, "hooks.log")
summary_path = os.path.join(subsystem_dir, "run-summary.json")

sys.path.insert(0, claude_dir)
from utils.log import make_logger  # noqa: E402

log = make_logger("observe-session-health", Path(subsystem_dir) / "hooks.log")

if not os.path.exists(summary_path):
    log("skip: no run-summary.json found")
    sys.exit(0)

with open(summary_path) as f:
    summary = json.load(f)

skill = summary.get("skill", "")

# Fuzzy-match skill name against pipeline spec filenames.
# "anki-add-cards" → looks for a spec whose stem is a suffix of the skill name.
specs = glob.glob(os.path.join(claude_dir, "pipeline-specifications", "*.md"))
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
