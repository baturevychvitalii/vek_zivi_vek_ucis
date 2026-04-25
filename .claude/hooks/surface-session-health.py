import json, os, sys
from datetime import datetime, timedelta

sys.stdin.read()

hooks_dir = os.path.dirname(os.path.abspath(__file__))
claude_dir = os.path.dirname(hooks_dir)
agent_dir = os.path.join(claude_dir, "agents", "health-agent")
findings_path = os.path.join(agent_dir, "health-findings.jsonl")
state_path = os.path.join(agent_dir, "health-state.json")

if not os.path.exists(findings_path):
    sys.exit(0)

unreviewed = []
with open(findings_path) as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        if entry.get("status") == "unreviewed":
            unreviewed.append(entry)

if not unreviewed:
    sys.exit(0)

state = {}
if os.path.exists(state_path):
    with open(state_path) as f:
        state = json.load(f)

last_nudged = state.get("last_nudged")
if last_nudged:
    delta = datetime.now() - datetime.fromisoformat(last_nudged)
    if delta < timedelta(days=7):
        sys.exit(0)

state["last_nudged"] = datetime.now().isoformat()
with open(state_path, "w") as f:
    json.dump(state, f, indent=2)

n = len(unreviewed)
skills = list({e.get("skill", "unknown") for e in unreviewed})
skills_str = ", ".join(skills)

output = {
    "hookSpecificOutput": {
        "hookEventName": "UserPromptSubmit",
        "additionalContext": (
            f"The health agent has {n} unreviewed observation(s) from recent skill runs "
            f"({skills_str}). Mention this briefly to the user — one sentence, no action required. "
            "They can ask the health agent for a summary whenever they want."
        )
    }
}

print(json.dumps(output))
