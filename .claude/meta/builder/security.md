# Skill Security Guide

Read this before creating or modifying any skill in `.claude/commands/`.

## Core Rule: One Command Per Bash Block

Each bash block in a skill must contain exactly one command. Never chain with `&&`, `;`, or `|`.

**Wrong:**
```bash
echo "$(pwd)" && date +%Y-%m-%d
```

**Right:**
```bash
pwd
```
```bash
date +%Y-%m-%d
```

**Why:** The permissions system matches the full command string against whitelist rules. Compound commands never match individual entries — they always fall through to a user prompt.

---

## Whitelist Contract

The whitelist in `.claude/settings.json` covers commands that run **every time a skill is invoked**. When you add a repeatable command to a skill, add its whitelist entry at the same time.

One-time setup commands (e.g., creating a directory on first run) should **not** be whitelisted. It is intentional that the user is prompted for these — they happen rarely and the confirmation is a useful signal.

The current set of whitelisted rules is the source of truth: `.claude/settings.json`.

---

## Git Policy

`git add`, `git commit`, and `git push` must **never** be run by Claude in this project — not even when asked generically. All git staging, committing, and pushing is the user's responsibility exclusively. Do not suggest or offer to run these commands.

Read-only git commands (`git log`, `git diff`, `git status`) are fine and whitelisted.

---

## What Always Requires a Prompt (Do Not Whitelist)

These must never be added to the allow list — they should always surface for user confirmation:

- One-time setup steps (directory creation, initial config, etc.)
- Destructive operations: `rm`, `git reset`, `git checkout --`, `git clean`
- Any `git` command that stages, commits, or pushes changes
- Writes outside `/tmp` and the project tree
- Any command that modifies shared state outside this project

---

## Pipeline Authoring

Pipelines live in `.claude/pipelines/`. Each step must be tagged `[mandatory]` or `[optional]` — no untagged steps allowed.

- `[mandatory]` — stop immediately on failure, notify user with step name and error
- `[optional]` — notify user with step name and error, ask whether to continue
- Never silently swallow failures
- Only compose existing `anki-skill-*` commands — no inline logic in pipeline definitions
- Pipeline steps must follow the same security rules as atomic skills

Pipeline entry points (thin wrappers) live in `.claude/commands/` with the `anki-pipeline-` prefix.

---

## Checklist Before Saving a Skill

- [ ] Every bash block contains exactly one command
- [ ] Every command that runs on every invocation has a matching entry in `.claude/settings.json`
- [ ] One-time setup steps are left unwhitelisted (prompt is intentional)
- [ ] No destructive commands are present or whitelisted
- [ ] Writes are scoped to `/tmp` or the project tree
