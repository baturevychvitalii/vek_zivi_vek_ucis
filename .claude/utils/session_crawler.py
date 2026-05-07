import json
import re


def read_transcript(path):
    events = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return events


def extract_text(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                parts.append(block.get("text", ""))
        return "\n".join(parts)
    return ""


def _candidate_strings(ev):
    if ev.get("type") == "user":
        yield extract_text(ev.get("message", {}).get("content", ""))
        return
    if ev.get("type") == "assistant":
        content = ev.get("message", {}).get("content", [])
        if isinstance(content, list):
            for block in content:
                if isinstance(block, dict) and block.get("type") == "tool_use":
                    tool_input = block.get("input", {}) or {}
                    for key in ("file_path", "path", "pattern"):
                        val = tool_input.get(key, "")
                        if isinstance(val, str):
                            yield val


def matches(events, patterns):
    found = set()
    target = len(patterns)
    for ev in events:
        for s in _candidate_strings(ev):
            for pat in patterns:
                if pat.pattern in found:
                    continue
                if pat.search(s):
                    found.add(pat.pattern)
        if len(found) == target:
            break
    return found


def matched_any(events, patterns):
    return bool(matches(events, patterns))


_ARCHITECT_RE = re.compile(r"meta/architect/context\.md")
_BUILDER_RE = re.compile(r"meta/builder/context\.md")


def detect_mode(events):
    """Infer session mode from context files read: 'architect' | 'builder' | 'user'."""
    for ev in events:
        for s in _candidate_strings(ev):
            if _ARCHITECT_RE.search(s):
                return "architect"
            if _BUILDER_RE.search(s):
                return "builder"
    return "user"
