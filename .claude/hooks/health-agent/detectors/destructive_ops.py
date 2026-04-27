"""
Detects destructive or hook-bypass operations inside skill runs.
Builder rule: no rm -rf, --no-verify, --force on destructive targets.
"""
import re

BANNED = [
    (r"\brm\s+-[a-z]*r[a-z]*f\b|\brm\s+-[a-z]*f[a-z]*r\b", "rm -rf"),
    (r"--no-verify", "--no-verify"),
    (r"\bgit\s+push\s+.*--force\b", "git push --force"),
    (r"git\s+push\s+-f\b", "git push -f"),
    (r"--force-with-lease", "--force-with-lease (check context)"),
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
                    "rule": "destructive_ops",
                    "severity": "violation",
                    "evidence": cmd[:200],
                    "suggested_fix": (
                        f"'{label}' is a destructive or hook-bypassing operation. "
                        "Not permitted inside skill runs (builder/security.md)."
                    ),
                })
                break
    return findings
