"""
Detects git policy violations inside skill runs.
Builder rule: skills must not commit, push, stage, or destructively reset git state.
"""
import re

BANNED = [
    (r"\bgit\s+commit\b", "git commit"),
    (r"\bgit\s+push\b", "git push"),
    (r"\bgit\s+add\b", "git add"),
    (r"\bgit\s+stage\b", "git stage"),
    (r"\bgit\s+reset\s+--hard\b", "git reset --hard"),
    (r"\bgit\s+checkout\s+--\b", "git checkout --"),
    (r"\bgit\s+clean\b", "git clean"),
]


def detect(ctx):
    findings = []
    for tool in ctx["tool_uses"]:
        if tool.get("name") != "Bash":
            continue
        cmd = (tool.get("input") or {}).get("command", "")
        for pattern, label in BANNED:
            if re.search(pattern, cmd):
                findings.append({
                    "rule": "git_policy",
                    "severity": "violation",
                    "evidence": cmd[:200],
                    "suggested_fix": (
                        f"'{label}' is not allowed inside skills. "
                        "Git operations must stay outside skill/pipeline scope (builder/security.md)."
                    ),
                })
                break
    return findings
