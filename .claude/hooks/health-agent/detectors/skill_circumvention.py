"""
Detects when a skill invocation fails and Claude continues by reading the skill's
context/spec files and imitating the skill manually.

This is a behavioral anomaly — Claude is being creative, but it masks a broken skill
that should be fixed.
"""


def detect(ctx):
    findings = []
    tool_uses = ctx["tool_uses"]
    tool_results = ctx["tool_results"]

    # Build a map of tool_use id → result
    result_by_id = {r.get("tool_use_id") or r.get("id"): r for r in tool_results}

    # Find failed Skill invocations
    for i, tool in enumerate(tool_uses):
        if tool.get("name") != "Skill":
            continue
        tool_id = tool.get("id")
        result = result_by_id.get(tool_id)
        if not result or not result.get("is_error"):
            continue

        skill_name = (tool.get("input") or {}).get("skill", "unknown")
        error_content = result.get("content", "")
        if isinstance(error_content, list):
            error_content = " ".join(
                c.get("text", "") for c in error_content if isinstance(c, dict)
            )

        # Look for subsequent Read calls targeting context/spec files
        circumvention_reads = []
        for j in range(i + 1, len(tool_uses)):
            subsequent = tool_uses[j]
            if subsequent.get("name") != "Read":
                continue
            path = (subsequent.get("input") or {}).get("file_path", "")
            lower = path.lower()
            if any(kw in lower for kw in ("inheritable", "context", "spec", "commands")):
                circumvention_reads.append(path)

        if circumvention_reads:
            findings.append({
                "rule": "skill_circumvention",
                "severity": "anomaly",
                "evidence": (
                    f"Skill '{skill_name}' failed: {error_content[:150]}. "
                    f"Claude then read: {', '.join(circumvention_reads[:3])}"
                ),
                "suggested_fix": (
                    f"Skill '{skill_name}' is broken — Claude worked around it by reading "
                    "its spec directly. Investigate why the skill invocation failed and fix "
                    "the skill rather than relying on this workaround."
                ),
            })

    return findings
