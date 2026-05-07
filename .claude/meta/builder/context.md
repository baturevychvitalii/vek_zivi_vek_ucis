# Builder Mode

*Read this when creating, modifying, or deleting skills, pipelines, or pipeline
specifications. Not for everyday card operations or architectural decisions.*

---

## Entry Contract


Before modifying any file under `.claude/` read:
    - `.claude/meta/builder/utilities.md`
    - `.claude/meta/builder/security.md`
    - `.claude/meta/builder/user_experience.md`

## What Builder Mode Covers

- Creating or modifying skills (`.claude/commands/skill/`)
- Creating or modifying pipeline entry points (`.claude/commands/pipe/`)
- Creating or modifying pipeline specifications (`.claude/pipeline-specifications/`)
- Updating the permissions whitelist in `.claude/settings.json`

## What Builder Mode Does Not Cover

- Adding cards, running pipelines, or other operational tasks (user mode)
- Changing how the system grows, adding new layers or primitives (out of scope for builder)

## Project State

Read `.claude/meta/memory/context.md` on entry.
