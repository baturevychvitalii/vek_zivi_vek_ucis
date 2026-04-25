import json, os, sys
from datetime import datetime

sys.stdin.read()

hooks_dir = os.path.dirname(os.path.abspath(__file__))
claude_dir = os.path.dirname(hooks_dir)
agent_dir = os.path.join(claude_dir, "agents", "health-agent")
os.makedirs(agent_dir, exist_ok=True)
summary_path = os.path.join(hooks_dir, "run-summary.json")

if not os.path.exists(summary_path):
    sys.exit(0)

with open(summary_path) as f:
    summary = json.load(f)

if not summary.get("completed_at"):
    sys.exit(0)

transcript_path = summary.get("transcript_path", "")
skill = summary.get("skill", "unknown")

if not transcript_path or not os.path.exists(transcript_path):
    sys.exit(0)

findings = []
with open(transcript_path) as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue

        if event.get("type") == "tool_result" and event.get("is_error"):
            content = event.get("content", "")
            if isinstance(content, list):
                content = " ".join(c.get("text", "") for c in content if isinstance(c, dict))
            findings.append({
                "id": f"{skill}-{datetime.now().isoformat()}",
                "timestamp": summary.get("completed_at"),
                "skill": skill,
                "error": content[:300],
                "status": "unreviewed"
            })

if not findings:
    sys.exit(0)

findings_path = os.path.join(agent_dir, "health-findings.jsonl")
with open(findings_path, "a") as f:
    for finding in findings:
        f.write(json.dumps(finding) + "\n")
