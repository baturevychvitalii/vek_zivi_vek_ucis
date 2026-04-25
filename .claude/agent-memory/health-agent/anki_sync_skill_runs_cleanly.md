---
name: anki-sync skill execution is clean
description: anki-sync skill runs without permission prompts, errors, or non-zero exit codes
type: project
---

**Observation:** The anki-sync skill defined in `.claude/skills/anki-sync/SKILL.md` executes cleanly:
- No permission prompts during execution
- No non-zero Bash exit codes
- No tool errors or failures
- Completes successfully in ~23 seconds
- Properly whitelisted: `Bash(python3 .claude/scripts/anki.py:*)` in .claude/settings.json

**Context:** The skill was invoked directly (without "/" prefix) because the skill spec has `#disable-model-invocation: true` commented out (line 4), which enables direct invocation.

**How to apply:** anki-sync is a well-formed skill. If user reports friction with health analysis around anki-sync runs, the friction is from the hooks/subagent infrastructure, not from the skill itself.
