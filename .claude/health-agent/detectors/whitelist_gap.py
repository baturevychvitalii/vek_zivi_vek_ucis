"""
Detects missing allowlist entries by comparing permission events against settings.json.
Suggests the exact allowlist string to add.
"""
import json, os, re


def _load_settings(claude_dir):
    path = os.path.join(claude_dir, "settings.json")
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return {}


def _allowlist_entries(settings):
    return settings.get("permissions", {}).get("allow", [])


def _matches_any(tool_name, detail, entries):
    for entry in entries:
        m = re.match(r"^(\w+)\((.+)\)$", entry)
        if not m:
            continue
        entry_tool, pattern = m.group(1), m.group(2)
        if entry_tool != tool_name:
            continue
        # strip trailing :* wildcard to get prefix
        if pattern.endswith(":*"):
            prefix = pattern[:-2]
            if detail.startswith(prefix):
                return True
        elif pattern.endswith("*"):
            prefix = pattern[:-1]
            if detail.startswith(prefix):
                return True
        elif detail == pattern:
            return True
    return False


def _suggest_entry(tool_name, detail):
    # Heuristic: use the command up to first variable-looking arg as the prefix
    # e.g. "python3 .claude/scripts/foo.py arg1" → "Bash(python3 .claude/scripts/foo.py:*)"
    if tool_name == "Bash":
        parts = detail.split()
        # find where arguments start (after the script/binary path)
        if len(parts) >= 2 and (parts[0] in ("python3", "python", "node", "bash", "sh")):
            prefix = " ".join(parts[:2])
        else:
            prefix = parts[0] if parts else detail
        return f'Bash({prefix}:*)'
    elif tool_name in ("Read", "Write", "Edit", "Glob", "Grep"):
        # strip to directory or use wildcard
        if detail:
            base = re.sub(r"/[^/]+$", "/*", detail)
            return f"{tool_name}({base})"
    return f"{tool_name}({detail})"


def detect(ctx):
    findings = []
    settings = _load_settings(ctx["claude_dir"])
    entries = _allowlist_entries(settings)

    for ev in ctx["permission_events"]:
        tool_name = ev.get("tool_name", "")
        detail = ev.get("detail") or tool_name
        if not tool_name or not detail:
            continue
        if _matches_any(tool_name, detail, entries):
            continue
        suggested = _suggest_entry(tool_name, detail)
        findings.append({
            "rule": "whitelist_gap",
            "severity": "warning",
            "evidence": f"{tool_name}({detail})",
            "suggested_fix": f'Add to settings.json allowlist: "{suggested}"',
        })
    return findings
