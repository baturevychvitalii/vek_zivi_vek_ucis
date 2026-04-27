"""
Detects bash command chaining violations.
Builder rule: each Bash tool call must contain exactly one command — no &&, ;, or |.
"""
import re


def detect(ctx):
    findings = []
    for tool in ctx["tool_uses"]:
        if tool.get("name") != "Bash":
            continue
        cmd = (tool.get("input") or {}).get("command", "")
        if not cmd:
            continue

        chains = []
        if "&&" in cmd:
            chains.append("&&")
        if re.search(r"(?<![|])\|\|", cmd):
            chains.append("||")
        # semicolons outside quoted strings (rough check)
        if re.search(r'(?<!["\']);\s*\S', cmd):
            chains.append(";")
        # pipe (lower severity — could be legitimate filtering)
        if "|" in cmd and "&&" not in cmd and ";" not in cmd:
            findings.append({
                "rule": "bash_chaining_pipe",
                "severity": "warning",
                "evidence": cmd[:200],
                "suggested_fix": "Split into separate Bash tool calls; pipe is disallowed by builder/bash-commands.md",
            })
            continue

        if chains:
            findings.append({
                "rule": "bash_chaining",
                "severity": "violation",
                "evidence": cmd[:200],
                "suggested_fix": (
                    f"Operators {chains} found. Split into separate Bash tool calls per "
                    "builder/bash-commands.md — one command per block."
                ),
            })
    return findings
