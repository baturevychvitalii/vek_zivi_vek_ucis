---
name: Hooks create analysis friction for health checking
description: Health observation hooks trigger subagent analysis and Python script executions that may exceed user expectations
type: project
---

**Pattern observed:** The health observation hooks in `.claude/hooks/` (observe-skill-start-natural.py, observe-session-health.py, surface-session-health.py) are designed to:
1. Detect when a skill runs (via PostToolUse Skill hook)
2. Create a run-summary.json file with skill metadata
3. On the next user prompt, surface a message instructing Claude to invoke the health-agent subagent
4. The subagent analyzes the run-summary and transcript

**User friction point:** When the health-agent begins analysis, it may execute Python scripts to parse and examine transcripts. These executions require permission prompts, which the user perceives as excessive ("I have approved more than 5 python script invocations...for what reason?").

**Why:** The health-agent has legitimate need to examine transcripts and pipeline specs, but each execution requires permission. The current approach doesn't batch or cache analysis results.

**How to apply:** If the user complains about health-check friction, consider:
1. Whether health analysis should run asynchronously (not on next prompt)
2. Whether the health-agent should operate with a broader whitelist for read-only analysis
3. Whether run-summary.json should be pre-analyzed by the hooks themselves before the subagent is invoked
