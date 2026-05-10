---
name: Debug sessions tend toward bash chaining
description: When troubleshooting, operators like &&, ||, and | appear in commands despite whitelist rules
type: feedback
---

Debug sessions often produce bash chaining violations (&&, ||, |) when trying to:
- Check file existence conditionally (`ls file && cat file || echo missing`)
- Filter command output (`grep pattern file | sort | uniq -c`)
- Sequence checks (`ls file 2>/dev/null && echo exists`)

**Why:** Under time pressure, chaining is the quick way to express conditional logic. The permission system's literal matching requirement isn't top-of-mind during debugging.

**How to apply:** When analyzing health findings from debug sessions, note that violations clustered in 1-2 minute windows with similar patterns (file checks, output filtering) are likely debug artifacts, not skill implementation issues. Flag them as confirmed_violation to maintain rule integrity, but surface nudges carefully — the issue is developer behavior in one session, not a systemic skill problem.
