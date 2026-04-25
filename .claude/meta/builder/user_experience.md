# User Experience Principles

*Read this when building or modifying anything that the user interacts with in
user mode — pipelines, skills, hooks, or any operational flow.*

---

## The Standard

Pipelines are the user's primary interface. A clean run — no prompts, no errors,
no unexpected pauses — is the baseline expectation. Any deviation is a defect.

---

## Smoothness Checklist

Before shipping a skill or pipeline change, verify:

**No permission friction**
- Every command that runs on every invocation is in the `settings.json` allow list
- All paths are project-root-relative (never absolute) — see `.claude/rules/portability.md`
- No chained commands (`&&`, `;`, `|`) — each bash block is exactly one command
  — see `.claude/rules/bash-commands.md`

**No unexpected pauses**
- One-time setup steps are intentionally left unwhitelisted (user confirmation is
  correct behavior for rare, significant operations)
- Repeated operations are always whitelisted (prompting the user on every run is friction)

**Predictable behavior**
- Skills produce consistent output given the same input
- Failures are surfaced clearly — never swallowed silently
- Optional steps are tagged `[optional]`; mandatory steps are tagged `[mandatory]`

---

## When Something Is Rough

If a pipeline produces friction (prompts, errors, pauses), diagnose before patching:
1. Is it a missing allowlist entry?
2. Is it a path format issue (absolute vs. relative)?
3. Is it a command chaining issue?
4. Is it a genuine one-time setup step (leave it unwhitelisted)?

Propose the minimal fix. Don't over-whitelist.
