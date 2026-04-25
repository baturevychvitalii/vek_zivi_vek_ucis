---
name: Health hooks should exclude infrastructure edits
description: Health findings should not report permission friction for edits to hook files themselves
type: feedback
---

**Rule:** The health analysis hooks (detect-health-issues.py) should filter out permission events that involve editing `.claude/hooks/` files when building findings.

**Why:** The health observation system detects permission prompts during skill runs and attributes them to that skill. But when developers/builders are actively modifying the hook infrastructure in the same transcript session where a skill runs, permission events for those edits get incorrectly attributed as user-facing friction. This creates false positives in the health findings — the friction is infrastructure development, not skill friction. This causes confusion and distracts from real issues.

**How to apply:** Before shipping a fix to detect-health-issues.py, add a filter in the permission event analysis (lines 54-80) to exclude any permission event where the `detail` path contains `.claude/hooks/`. Infrastructure changes are not user-facing friction.
