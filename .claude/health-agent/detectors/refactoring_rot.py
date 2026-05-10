"""
Detects broken file/skill references introduced during skill or pipeline edits.
Catches the common refactoring failure: a name is changed in one place but
references elsewhere are forgotten.
"""
import os, re


_PATH_RE = re.compile(r"""['"`](\.(\.)?/[\w./-]+\.\w+)['"`]|['"`](\.claude/[\w./-]+)['"`]""")
_SKILL_REF_RE = re.compile(r"""skill:\s*['"]?([\w:/-]+)['"]?""")
_BASH_SCRIPT_RE = re.compile(r"""python3?\s+(\.claude/[\w./-]+\.py)""")


def _extract_refs(content):
    refs = set()
    for m in _PATH_RE.finditer(content):
        p = m.group(1) or m.group(3)
        if p:
            refs.add(p)
    for m in _BASH_SCRIPT_RE.finditer(content):
        refs.add(m.group(1))
    return refs


def _extract_skill_names(content):
    names = set()
    for m in _SKILL_REF_RE.finditer(content):
        names.add(m.group(1))
    return names


def _resolve(ref, claude_dir):
    project_root = os.path.dirname(claude_dir)
    return os.path.normpath(os.path.join(project_root, ref))


def _skill_exists(name, claude_dir):
    commands_dir = os.path.join(claude_dir, "commands")
    candidates = [
        os.path.join(commands_dir, name + ".md"),
        os.path.join(commands_dir, name.replace(":", "/") + ".md"),
        os.path.join(commands_dir, name.replace("pipe:", "pipe/") + ".md"),
    ]
    return any(os.path.exists(c) for c in candidates)


_EDIT_TARGETS = (".claude/commands/", ".claude/pipeline-specifications/", ".claude/agents/", ".claude/health-agent/")


def detect(ctx):
    findings = []
    claude_dir = ctx["claude_dir"]

    for tool in ctx["tool_uses"]:
        if tool.get("name") not in ("Edit", "Write"):
            continue
        inp = tool.get("input") or {}
        file_path = inp.get("file_path", "")
        if not any(t in file_path for t in _EDIT_TARGETS):
            continue

        content = inp.get("content") or inp.get("new_string") or ""
        if not content:
            continue

        broken = []

        for ref in _extract_refs(content):
            resolved = _resolve(ref, claude_dir)
            if not os.path.exists(resolved):
                broken.append(f"missing path: {ref}")

        for skill_name in _extract_skill_names(content):
            if not _skill_exists(skill_name, claude_dir):
                broken.append(f"missing skill: {skill_name}")

        if broken:
            findings.append({
                "rule": "refactoring_rot",
                "severity": "warning",
                "evidence": f"In {file_path}: {'; '.join(broken[:5])}",
                "suggested_fix": (
                    "References to non-existent files or skills detected after edit. "
                    "Likely a refactoring artifact — update the broken references."
                ),
            })

    return findings
