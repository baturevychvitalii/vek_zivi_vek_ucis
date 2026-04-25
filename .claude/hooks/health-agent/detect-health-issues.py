import json, os, sys
from datetime import datetime, timezone

hooks_dir = os.path.dirname(os.path.abspath(__file__))
claude_dir = os.path.dirname(os.path.dirname(hooks_dir))
agent_dir = os.path.join(claude_dir, "agents", "health-agent")
summary_path = os.path.join(hooks_dir, "run-summary.json")
events_path = os.path.join(hooks_dir, "permission-events.jsonl")
findings_path = os.path.join(agent_dir, "health-findings.jsonl")


def parse_utc(ts):
    ts = ts.rstrip("Z")
    return datetime.fromisoformat(ts).replace(tzinfo=timezone.utc)


def analyze(summary):
    skill = summary.get("skill", "unknown")
    transcript_path = summary.get("transcript_path", "")
    started_at = parse_utc(summary["started_at"])

    findings = []

    # Tool errors from transcript, scoped to skill window
    if transcript_path and os.path.exists(transcript_path):
        with open(transcript_path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue
                ts = event.get("timestamp")
                if ts and parse_utc(ts) < started_at:
                    continue
                if event.get("type") == "tool_result" and event.get("is_error"):
                    content = event.get("content", "")
                    if isinstance(content, list):
                        content = " ".join(
                            c.get("text", "") for c in content if isinstance(c, dict)
                        )
                    findings.append({
                        "id": f"{skill}-error-{datetime.utcnow().isoformat()}Z",
                        "timestamp": datetime.utcnow().isoformat() + "Z",
                        "skill": skill,
                        "type": "tool_error",
                        "error": content[:300],
                        "status": "unreviewed",
                    })

    # Permission prompts from sidecar, scoped to skill window
    if os.path.exists(events_path):
        prompts = []
        with open(events_path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    ev = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if ev.get("transcript_path") != transcript_path:
                    continue
                ev_ts = ev.get("timestamp", "")
                if ev_ts and parse_utc(ev_ts) < started_at:
                    continue
                detail = ev.get("detail") or ev.get("tool_name", "")
                if "/.claude/" in detail or detail.startswith(".claude/"):
                    continue
                prompts.append(ev)
        if prompts:
            findings.append({
                "id": f"{skill}-permissions-{datetime.utcnow().isoformat()}Z",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "skill": skill,
                "type": "permission_friction",
                "error": f"{len(prompts)} permission prompt(s): "
                    + ", ".join(p.get("detail") or p.get("tool_name", "") for p in prompts),
                "status": "unreviewed",
            })

    if not findings:
        return

    os.makedirs(agent_dir, exist_ok=True)
    with open(findings_path, "a") as f:
        for finding in findings:
            f.write(json.dumps(finding) + "\n")


def load_summary():
    if not os.path.exists(summary_path):
        return None
    try:
        with open(summary_path) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def mark_analyzed(summary):
    summary["analyzed_at"] = datetime.utcnow().isoformat() + "Z"
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)


# Detect invocation context: UserPromptSubmit provides JSON on stdin with "prompt";
# Stop hook provides non-JSON (or empty) stdin.
raw = sys.stdin.read()
try:
    inp = json.loads(raw)
    # UserPromptSubmit path — only analyze when a new skill is starting
    prompt = inp.get("prompt", "").strip()
    if not prompt.startswith("/"):
        sys.exit(0)
    summary = load_summary()
    if not summary or summary.get("analyzed_at") or not summary.get("started_at"):
        sys.exit(0)
    analyze(summary)
    mark_analyzed(summary)
except (json.JSONDecodeError, ValueError):
    # Stop path — analyze any pending unanalyzed skill
    summary = load_summary()
    if not summary or summary.get("analyzed_at") or not summary.get("started_at"):
        sys.exit(0)
    analyze(summary)
    mark_analyzed(summary)
